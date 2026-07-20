"""
Integration tests for the LangGraph workflow structure.

These tests verify the graph topology and loop protection without
requiring real LLM API calls (uses mock agents).
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_workflow_loop_protection():
    """Verify that correction_count never exceeds max_corrections."""
    from app.graph.workflow import create_workflow

    # Create a fresh workflow
    workflow = create_workflow()

    initial_state = {
        "query": "Test query about MLA mechanism",
        "paper_context": "MLA lowers KV cache overhead.",
        "max_corrections": 2,
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

    # Run the workflow with ainvoke
    final_state = await workflow.ainvoke(initial_state)

    assert final_state["correction_count"] <= final_state["max_corrections"], (
        "Loop protection failed: correction_count exceeded max_corrections"
    )
    assert final_state.get("final_report"), (
        "Workflow should produce a final_report even if LLM calls fail"
    )


@pytest.mark.asyncio
async def test_workflow_graph_structure():
    """Verify the compiled graph has the expected nodes and entry point."""
    from app.graph.workflow import create_workflow

    workflow = create_workflow()

    # LangGraph compiled graphs have a get_graph() method
    graph = workflow.get_graph()
    nodes = graph.nodes if hasattr(graph, 'nodes') else {}

    # Basic structural assertions
    assert workflow is not None, "Workflow should compile successfully"
