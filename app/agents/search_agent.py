"""
Search Agent — Hybrid RAG retrieval (Milvus + BM25 + Cross-Encoder rerank).

Embeds the user query, runs dense + sparse search in parallel, fuses results,
and re-ranks with a Cross-Encoder for high-quality context retrieval.

Uses HuggingFace mirror for faster model downloads in China.
Set HF_ENDPOINT env var to override (e.g. https://hf-mirror.com).
"""
import logging
import os

from app.graph.state import GraphState
from app.services.retriever import get_retriever

logger = logging.getLogger("miemie.search")

# Use HF mirror for faster downloads from China (can be overridden via env)
if not os.getenv("HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


class SearchAgent:
    """Hybrid RAG retrieval agent (Milvus dense + BM25 sparse + Cross-Encoder rerank)."""

    def __init__(self):
        self._initialized = False

    def _lazy_init(self) -> bool:
        """Lazy-load retriever and verify it has data."""
        if self._initialized:
            return True

        try:
            self.retriever = get_retriever()
            corpus_size = self.retriever.get_corpus_size()
            if corpus_size == 0:
                logger.warning(
                    "Milvus collection is empty. Run 'python mcp_server/ingest_docs.py' first."
                )
            self._initialized = True
            return True
        except Exception as exc:
            logger.error("Failed to initialize hybrid retriever: %s", exc)
            return False

    async def run(self, state: GraphState) -> dict:
        query = state.get("query", "")

        if not self._lazy_init():
            logger.warning("SearchAgent running in passthrough mode")
            return self._passthrough(state)

        logger.info("SearchAgent running hybrid retrieval for: %s...", query[:80])

        try:
            docs = self.retriever.retrieve(query, top_k=4)

            if not docs:
                context = "未检索到高度相关的背景知识，请大模型基于自身知识库推演。"
                logger.warning("No relevant documents found")
            else:
                context = "\n\n".join(
                    f"【高相关片段 {i+1}】: {doc.page_content}"
                    for i, doc in enumerate(docs)
                )
                logger.info("SearchAgent retrieved %d documents", len(docs))

            new_log = {
                "agent": "Search Agent",
                "content": (
                    f"混合检索（Milvus Dense + BM25 Sparse + Cross-Encoder）完成，"
                    f"从 {self.retriever.get_corpus_size()} 篇文档中检索到 {len(docs)} 个高价值技术切片。"
                ),
            }

            return {
                "search_output": {"context": context},
                "paper_context": context,
                "history_logs": state.get("history_logs", []) + [new_log],
            }

        except Exception as exc:
            logger.error("SearchAgent retrieval failed: %s", exc)
            return self._passthrough(state)

    def _passthrough(self, state: GraphState) -> dict:
        """Fallback: let the LLM answer from its own knowledge."""
        new_log = {
            "agent": "Search Agent",
            "content": "混合检索跳过，LLM 将基于自身知识库进行推演。",
        }
        return {
            "search_output": {"context": ""},
            "paper_context": "未启用 RAG 检索，请基于通用知识回答。",
            "history_logs": state.get("history_logs", []) + [new_log],
        }
