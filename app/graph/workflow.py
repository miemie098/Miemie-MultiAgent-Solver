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
def _degraded_verdict(persona: str, exc: Exception) -> Dict:
    """Return a neutral "service unavailable" verdict for a failed critic.

    This is NOT a vote against the analysis — it's an explicit abstention.
    The Moderator knows to discount degraded votes from its quorum count.
    """
    return {
        "passed": False,
        "confidence": 0.0,
        "key_concerns": [f"[{persona}] 服务暂不可用 ({type(exc).__name__})，该审查员弃权"],
        "suggested_fix": "",
        "degraded": True,  # signal to Moderator: this is a fault, not a real vote
    }


async def _retry_critic(critic, query: str, analysis: str,
                         max_retries: int = 3, base_delay: float = 1.0) -> Dict:
    """Node-level retry for a single critic with exponential backoff.

    On transient failure, retries with 1s→2s→4s backoff.
    On final exhaustion, returns a degraded abstention verdict — does NOT
    throw, so asyncio.gather always converges and the Moderator always runs.

    Search and Analyze results are untouched throughout.
    """
    persona = critic.__class__.__name__

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                logger.info("%s retry %d/%d ...", persona, attempt, max_retries - 1)
            return await critic.critique(query, analysis)
        except Exception as exc:
            remaining = max_retries - 1 - attempt
            if remaining <= 0:
                logger.error(
                    "%s exhausted all %d retries — returning degraded verdict", persona, max_retries
                )
                return _degraded_verdict(persona, exc)
            wait = base_delay * (2 ** attempt)  # 1s, 2s, 4s
            logger.warning(
                "%s attempt %d/%d failed (%s), retrying in %.1fs ...",
                persona, attempt + 1, max_retries, exc, wait,
            )
            await asyncio.sleep(wait)


async def _debate_critic(state: GraphState) -> Dict[str, Any]:
    """Run 3 critic personas in parallel with node-level retry + graceful degradation."""
    from app.agents.debate_critics import OptimistCritic, SkepticCritic, RealistCritic
    from app.agents.moderator_agent import ModeratorAgent

    query = state.get("query", "")
    analysis = state.get("analyzer_output", {}).get("analysis", "")
    current_count = state.get("correction_count", 0)

    logger.info("Debate mode: launching 3 parallel critics (each with up to 3 retries)...")

    optimist = OptimistCritic()
    skeptic = SkepticCritic()
    realist = RealistCritic()
    moderator = ModeratorAgent()

    # Fan-out: all 3 critics run in parallel, each independently retries.
    # _retry_critic never throws — degraded critics return abstention verdicts.
    critiques = await asyncio.gather(
        _retry_critic(optimist, query, analysis),
        _retry_critic(skeptic,  query, analysis),
        _retry_critic(realist,  query, analysis),
    )

    degraded_count = sum(1 for c in critiques if c.get("degraded"))
    healthy_count = 3 - degraded_count

    if degraded_count == 3:
        # Complete outage — escalate, no meaningful vote possible
        logger.error("All 3 critics degraded — DeepSeek service unreachable")
        raise RuntimeError(
            "辩论模式无法继续：3 个审查节点全部不可用。"
            "请检查 DeepSeek API 服务状态或网络连接后重试。"
        )
    elif degraded_count > 0:
        logger.warning(
            "%d/%d critics degraded — running Moderator with %d healthy votes",
            degraded_count, 3, healthy_count,
        )

    # Fan-in: moderator synthesizes (handles degraded votes gracefully)
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
