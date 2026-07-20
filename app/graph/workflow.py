"""
LangGraph workflow definition — directed cyclic graph with 5 agent nodes.

Topology:
    search -> analyzer -> critic -+-> summary -> END
                        ^         |
                        |         +-> compactor (on rejection)
                        +------------+

Supports two critic modes via DEBATE_MODE env var:
  - "single" (default): one CriticAgent reviews the analysis
  - "debate": 3 persona-based critics + Moderator synthesize consensus
"""
import asyncio
import logging
import os
from typing import Dict, Any

from langgraph.graph import StateGraph, END

from app.graph.state import GraphState
from app.agents.search_agent import SearchAgent
from app.agents.analyzer_agent import AnalyzerAgent
from app.agents.critic_agent import CriticAgent
from app.agents.compactor_agent import CompactorAgent
from app.agents.summary_agent import SummaryAgent

logger = logging.getLogger("miemie.workflow")

# Which critic mode to use — "single" or "debate"
DEBATE_MODE = os.getenv("DEBATE_MODE", "single").lower()


def create_workflow():
    """Build and compile the multi-agent reflective workflow graph."""
    workflow = StateGraph(GraphState)

    # --- Instantiate agents ---
    search_agent = SearchAgent()
    analyzer = AnalyzerAgent()
    critic = CriticAgent()
    compactor = CompactorAgent()
    summary_agent = SummaryAgent()

    # --- Node definitions ---
    async def search_node(state: GraphState) -> Dict[str, Any]:
        return await search_agent.run(state)

    async def analyzer_node(state: GraphState) -> Dict[str, Any]:
        return await analyzer.run(state)

    async def critic_node(state: GraphState) -> Dict[str, Any]:
        """Critic node — dispatches to single or debate mode."""
        if DEBATE_MODE == "debate":
            return await _debate_critic(state)
        return await critic.run(state)

    async def compactor_node(state: GraphState) -> Dict[str, Any]:
        history = state.get("history_logs", [])
        original_ctx = (
            state.get("search_output", {}).get("context")
            or state.get("paper_context", "")
        )
        compressed = await compactor.compress(history, original_ctx)

        return {
            "compressed_context": compressed,
            "compactor_output": {"status": "sharding_success"},
            "history_logs": state.get("history_logs", [])
            + [{"agent": "Compactor Agent", "content": "已执行语义上下文压缩。"}],
        }

    async def summary_node(state: GraphState) -> Dict[str, Any]:
        return await summary_agent.run(state)

    # --- Register nodes ---
    workflow.add_node("search", search_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("compactor", compactor_node)
    workflow.add_node("summary", summary_node)

    # --- Edges ---
    workflow.set_entry_point("search")
    workflow.add_edge("search", "analyzer")
    workflow.add_edge("analyzer", "critic")

    # --- Conditional routing ---
    def router(state: GraphState) -> str:
        critic_res = state.get("critic_output", {})
        if (
            critic_res.get("passed")
            or state["correction_count"] >= state["max_corrections"]
        ):
            return "to_summary"
        return "to_retry"

    workflow.add_conditional_edges(
        "critic",
        router,
        {"to_summary": "summary", "to_retry": "compactor"},
    )

    workflow.add_edge("compactor", "analyzer")
    workflow.add_edge("summary", END)

    logger.info("Workflow compiled (critic_mode=%s)", DEBATE_MODE)
    return workflow.compile()


# ---------------------------------------------------------------------------
# Debate mode internals
# ---------------------------------------------------------------------------
async def _debate_critic(state: GraphState) -> Dict[str, Any]:
    """Run 3 critic personas in parallel, then moderate the results."""
    from app.agents.debate_critics import OptimistCritic, SkepticCritic, RealistCritic
    from app.agents.moderator_agent import ModeratorAgent

    query = state.get("query", "")
    analysis = state.get("analyzer_output", {}).get("analysis", "")
    current_count = state.get("correction_count", 0)

    logger.info("Debate mode: launching 3 parallel critics...")

    optimist = OptimistCritic()
    skeptic = SkepticCritic()
    realist = RealistCritic()
    moderator = ModeratorAgent()

    # Fan-out: all 3 critics run in parallel
    critiques = await asyncio.gather(
        optimist.critique(query, analysis),
        skeptic.critique(query, analysis),
        realist.critique(query, analysis),
    )

    # Fan-in: moderator synthesizes
    result = await moderator.synthesize(query, analysis, critiques)

    passed = result["consensus"]
    status_text = "通过" if passed else "拒绝"

    new_log = {
        "agent": "Debate Panel",
        "content": (
            f"【{status_text}】3方审查完毕 (信心度: {result.get('confidence', 0):.2f})。"
            f" {result.get('feedback', '')[:200]}"
        ),
    }

    return {
        "critic_output": {
            "passed": passed,
            "feedback": result.get("feedback", ""),
            "debate_details": {
                "optimist": critiques[0],
                "skeptic": critiques[1],
                "realist": critiques[2],
                "moderator_verdict": result.get("feedback", ""),
            },
        },
        "history_logs": state.get("history_logs", []) + [new_log],
        "correction_count": current_count + 1,
    }
