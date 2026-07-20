"""
Search Agent — RAG retrieval from local ChromaDB vector store.

Embeds the user query and retrieves the top-k most relevant document chunks
from the ingested AI research papers and technical documentation.

Uses HuggingFace mirror for faster model downloads in China.
Set HF_ENDPOINT env var to override (e.g. https://hf-mirror.com).
"""
import logging
import os
import sys

from app.graph.state import GraphState
from app.agents.config import LLMFactory

logger = logging.getLogger("miemie.search")

# Use HF mirror for faster downloads from China (can be overridden via env)
if not os.getenv("HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


class SearchAgent:
    """RAG retrieval agent. Downloads the embedding model on first use."""

    def __init__(self):
        self._embeddings = None
        self._vectorstore = None
        self.llm = LLMFactory.get_llm(temperature=0.1)
        self._init_attempted = False

    def _lazy_init(self):
        """Lazy-load embeddings and vector store (downloads model on first call)."""
        if self._init_attempted:
            return self._vectorstore is not None
        self._init_attempted = True

        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma

            logger.info("Loading embedding model all-MiniLM-L6-v2 (first time may download ~80MB)...")
            self._embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
            )
            logger.info("Embedding model loaded successfully")

            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_dir = os.path.join(base_dir, "data", "chroma_db")

            self._vectorstore = Chroma(
                persist_directory=db_dir, embedding_function=self._embeddings
            )
            logger.info("ChromaDB connected, collection size: %d", self._vectorstore._collection.count())
            return True

        except Exception as e:
            logger.error("Failed to initialize vector search: %s", e)
            logger.warning("SearchAgent will run in passthrough mode (no RAG context)")
            return False

    async def run(self, state: GraphState) -> dict:
        query = state.get("query", "")

        # Try lazy init — if it fails, skip RAG and pass through
        if not self._lazy_init():
            logger.warning("SearchAgent running in passthrough mode")
            return self._passthrough(state)

        logger.info("SearchAgent retrieving context for: %s...", query[:80])

        try:
            docs = self._vectorstore.similarity_search(query, k=3)

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
                "content": f"成功从本地 ChromaDB 检索到 {len(docs)} 个高价值技术切片。",
            }

            return {
                "search_output": {"context": context},
                "paper_context": context,
                "history_logs": state.get("history_logs", []) + [new_log],
            }

        except Exception as e:
            logger.error("SearchAgent retrieval failed: %s", e)
            return self._passthrough(state)

    def _passthrough(self, state: GraphState) -> dict:
        """Fallback: let the LLM answer from its own knowledge."""
        new_log = {
            "agent": "Search Agent",
            "content": "向量检索跳过，LLM 将基于自身知识库进行推演。",
        }
        return {
            "search_output": {"context": ""},
            "paper_context": "未启用 RAG 检索，请基于通用知识回答。",
            "history_logs": state.get("history_logs", []) + [new_log],
        }
