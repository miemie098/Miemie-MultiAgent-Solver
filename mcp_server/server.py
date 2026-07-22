"""
MCP Knowledge Server — exposes hybrid retrieval as an MCP tool.

Uses the shared hybrid retriever (Milvus + BM25 + Cross-Encoder) so the MCP
server benefits from the same production-grade retrieval pipeline as the main app.
"""
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from app.services.retriever import get_retriever

# ── Lazy-load retriever ────────────────────────────────────────────────
_retriever = None


def _get_retriever():
    global _retriever
    if _retriever is None:
        if not os.getenv("HF_ENDPOINT"):
            os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        _retriever = get_retriever()
    return _retriever


# ── MCP server ─────────────────────────────────────────────────────────
mcp = FastMCP("Miemie-Knowledge-Server")


@mcp.tool()
def retrieve_ai_papers(query: str) -> str:
    """Search the local AI infrastructure knowledge base for relevant technical facts.

    Uses hybrid retrieval: Milvus dense search + BM25 sparse search
    fused and re-ranked with a Cross-Encoder for high precision.
    """
    try:
        retriever = _get_retriever()
        docs = retriever.retrieve(query, top_k=3)
        if not docs:
            return "未检索到相关内容。"
        return "\n".join(doc.page_content for doc in docs)
    except Exception as exc:
        return f"检索失败: {exc}"


@mcp.tool()
def get_knowledge_base_stats() -> str:
    """Return statistics about the knowledge base (document count, etc.)."""
    try:
        retriever = _get_retriever()
        size = retriever.get_corpus_size()
        return f"知识库共收录 {size} 个文本片段，覆盖 FlashAttention、vLLM、GPTQ、MoE 等 AI 基础设施主题。"
    except Exception as exc:
        return f"无法获取知识库状态: {exc}"
