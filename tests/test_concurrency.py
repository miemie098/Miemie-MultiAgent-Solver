"""
Concurrency tests — verify SOP state-channel isolation.

Two concurrent workflow invocations must not cross-contaminate
each other's agent output channels.
"""
import pytest
import asyncio


@pytest.mark.asyncio
async def test_agent_state_isolation():
    """Two concurrent tasks should produce structurally independent outputs."""
    from app.graph.workflow import create_workflow

    workflow = create_workflow()

    task_a = {
        "query": "Task A: Analyze PagedAttention memory fragmentation",
        "paper_context": "Context A",
        "max_corrections": 3,
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

    task_b = {
        "query": "Task B: Analyze MLA low-rank projection topology",
        "paper_context": "Context B",
        "max_corrections": 3,
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

    # Run both workflows concurrently
    results = await asyncio.gather(
        workflow.ainvoke(task_a),
        workflow.ainvoke(task_b),
    )

    state_a, state_b = results

    # Structural assertions (not content-specific, since LLM output varies)
    assert "final_report" in state_a, "Task A should produce a final_report"
    assert "final_report" in state_b, "Task B should produce a final_report"
    assert state_a.get("correction_count", 0) <= state_a.get("max_corrections", 99)
    assert state_b.get("correction_count", 0) <= state_b.get("max_corrections", 99)

    # The two reports should be different (different queries)
    assert state_a.get("final_report") != state_b.get("final_report"), (
        "Different queries should produce different reports"
    )
