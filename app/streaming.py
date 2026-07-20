"""
SSE (Server-Sent Events) streaming for real-time agent workflow visualization.

Uses ainvoke() for reliability, then replays the collected history_logs
as SSE events so the frontend can animate node-by-node.

Note: True node-by-node streaming requires LangGraph >= 0.3 with working
astream() support. This implementation works reliably with 0.2.x.
"""
import json
import logging
from typing import AsyncGenerator

from app.graph.workflow import create_workflow
from app.graph.state import GraphState

logger = logging.getLogger("miemie.streaming")

NODE_LABELS = {
    "search": "Search Agent",
    "analyzer": "Analyzer Agent",
    "critic": "Critic Agent",
    "compactor": "Compactor Agent",
    "summary": "Summary Agent",
}


async def stream_workflow(query: str, max_corrections: int = 3) -> AsyncGenerator[str, None]:
    """
    Execute workflow and stream results as SSE events.

    Sends each history_log entry as a 'node_complete' event with a small
    delay so the frontend animation plays smoothly.
    """
    workflow = create_workflow()

    initial_state: GraphState = {
        "query": query,
        "paper_context": "",
        "max_corrections": max_corrections,
        "correction_count": 0,
        "history_logs": [],
        "search_output": {},
        "analyzer_output": {},
        "critic_output": {},
        "compactor_output": {},
        "summary_output": {},
        "compressed_context": "",
        "final_report": "",
    }

    logger.info("Starting streaming workflow: %s...", query[:80])

    try:
        # Use ainvoke — reliable, works with all LangGraph versions
        result = await workflow.ainvoke(initial_state)

        history_logs = result.get("history_logs", [])
        final_report = result.get("final_report", "")
        correction_count = result.get("correction_count", 0)

        logger.info("Workflow complete — %d log entries, %d chars report",
                     len(history_logs), len(final_report))

        # Stream each log entry for frontend animation
        for log in history_logs:
            agent = log.get("agent", "Unknown")
            content = log.get("content", "")
            node = _guess_node(agent)
            yield _sse("node_complete", {
                "node": node,
                "agent": agent,
                "content": content,
            })

        # Final done event
        yield _sse("done", {
            "report": final_report,
            "correction_count": correction_count,
        })

    except Exception as exc:
        logger.error("Streaming workflow failed: %s", exc)
        yield _sse("error", {"message": str(exc)})


def _guess_node(agent: str) -> str:
    """Map agent name back to workflow node name."""
    for node, label in NODE_LABELS.items():
        if label in agent:
            return node
    return "unknown"


def _sse(event_type: str, data: dict) -> str:
    """Format an SSE event."""
    payload = {"type": event_type, **data}
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
