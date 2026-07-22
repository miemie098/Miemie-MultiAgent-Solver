"""
FastAPI server for Miemie-MultiAgent-Solver.
Serves the frontend dashboard and exposes the multi-agent workflow API.
"""
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.graph.workflow import create_workflow
from app.streaming import stream_workflow

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger("miemie.api")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Infra Multi-Agent Reflective Solver",
    description="LangGraph-powered multi-agent system for AI infrastructure analysis",
    version="0.2.0",
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class SolverRequest(BaseModel):
    query: str = Field(..., description="The AI infrastructure problem to analyze")
    max_corrections: int = Field(3, ge=1, le=10, description="Max critic-analysis rectification rounds")


class SolverResponse(BaseModel):
    status: str
    correction_count: int
    history_logs: list
    final_report: str


# ---------------------------------------------------------------------------
# Cached compiled workflow (created once at startup)
# ---------------------------------------------------------------------------
_workflow = None


def _get_workflow():
    """Lazy-init the compiled LangGraph workflow (singleton)."""
    global _workflow
    if _workflow is None:
        logger.info("Compiling LangGraph workflow...")
        _workflow = create_workflow()
        logger.info("Workflow compiled successfully.")
    return _workflow


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/")
async def get_frontend_dashboard():
    """Serve the frontend dashboard."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(html_path)


@app.post("/api/solve", response_model=SolverResponse)
async def solve_infra_problem(req: SolverRequest):
    """
    Execute the full multi-agent reflective workflow.

    Flow: Search → Analyze → Critic → (loop: Compactor → Analyze → Critic) → Summary
    """
    workflow = _get_workflow()

    initial_state = {
        "query": req.query,
        "paper_context": "",
        "max_corrections": req.max_corrections,
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

    logger.info(f"Starting workflow for query: {req.query[:100]}...")

    try:
        final_state = await workflow.ainvoke(initial_state)
    except Exception as exc:
        logger.error(f"Workflow execution failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Multi-agent workflow failed: {str(exc)}")

    correction_count = final_state.get("correction_count", 0)
    logger.info(
        f"Workflow complete — correction_count={correction_count}, "
        f"report_len={len(final_state.get('final_report', ''))}"
    )

    return SolverResponse(
        status="success",
        correction_count=correction_count,
        history_logs=final_state.get("history_logs", []),
        final_report=final_state.get("final_report", ""),
    )


@app.post("/api/solve/stream")
async def solve_stream(req: SolverRequest):
    """
    Execute the multi-agent workflow with real-time SSE streaming.

    Events:
      - node_start: {node: "analyzer"|"critic"|...}
      - node_complete: {node, agent, content}
      - done: {report, history_logs, correction_count}
      - error: {message}
    """
    return StreamingResponse(
        stream_workflow(req.query, req.max_corrections),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    workflow = _get_workflow()
    return {
        "status": "healthy",
        "workflow_compiled": workflow is not None,
    }
