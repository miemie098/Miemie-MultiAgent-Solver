"""
Hybrid retrieval service: Milvus Dense + BM25 Sparse + Cross-Encoder Rerank.

Replaces the previous ChromaDB-only search with a production-grade multi-way
retrieval pipeline, matching the technical depth of Miemie-Agent-RAG.
"""
import logging
import os

# Use HF mirror for faster downloads from China (set BEFORE importing HF modules)
if not os.getenv("HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# Suppress gRPC GOAWAY noise from Milvus embedded mode on Windows
os.environ.setdefault("GRPC_VERBOSITY", "ERROR")

from typing import List, Optional

import numpy as np
from pymilvus import MilvusClient, DataType
from langchain_huggingface import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

logger = logging.getLogger("miemie.retriever")

# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_retriever_instance: Optional["MiemieHybridRetriever"] = None


def get_retriever() -> "MiemieHybridRetriever":
    """Lazy-load the hybrid retriever singleton."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = MiemieHybridRetriever()
    return _retriever_instance


def _resolve_project_root() -> str:
    """Resolve project root regardless of cwd."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Lightweight document wrapper
# ---------------------------------------------------------------------------
class _Doc:
    """Minimal doc object compatible with .page_content attribute expected by callers."""

    __slots__ = ("page_content",)

    def __init__(self, page_content: str) -> None:
        self.page_content = page_content


# ---------------------------------------------------------------------------
# Hybrid Retriever
# ---------------------------------------------------------------------------
class MiemieHybridRetriever:
    """Multi-way hybrid retrieval with Cross-Encoder reranking.

    Pipeline: Dense (Milvus) + Sparse (BM25) → fusion → Cross-Encoder → top-k
    """

    COLLECTION_NAME = "miemie_infra_knowledge"
    EMBEDDING_DIM = 768  # all-mpnet-base-v2
    DEFAULT_TOP_K = 10
    FINAL_K = 4

    def __init__(
        self,
        fusion_method: str = "linear_weighted",
        fusion_alpha: float = 0.5,
    ) -> None:
        if fusion_method not in ("rrf", "linear_weighted"):
            raise ValueError(f"Unsupported fusion method: {fusion_method}")
        if not 0.0 <= fusion_alpha <= 1.0:
            raise ValueError(f"fusion_alpha must be in [0, 1], got {fusion_alpha}")

        self.fusion_method = fusion_method
        self.fusion_alpha = fusion_alpha

        project_root = _resolve_project_root()
        milvus_db_path = os.path.join(project_root, "data", "milvus.db")
        os.makedirs(os.path.dirname(milvus_db_path), exist_ok=True)

        # ── Embedding model (dense) — try mpnet first, fall back to MiniLM ──
        embedding_model = os.getenv(
            "EMBEDDING_MODEL_PATH", "sentence-transformers/all-mpnet-base-v2"
        )
        try:
            logger.info("Loading embedding model: %s", embedding_model)
            self.dense_embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={"device": "cpu"},
            )
        except Exception as exc:
            logger.warning("Failed to load %s: %s — falling back to all-MiniLM-L6-v2", embedding_model, exc)
            self.dense_embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
            )
        try:
            self._embedding_dim = self.dense_embeddings._client.get_embedding_dimension()
        except Exception:
            self._embedding_dim = getattr(self.dense_embeddings, "_embedding_dim", 768)
        logger.info("Embedding dim = %d", self._embedding_dim)

        # ── Milvus (embedded) ──
        self.client = MilvusClient(milvus_db_path)
        self._ensure_collection()

        # ── BM25 sparse index ──
        self.corpus: List[str] = []
        self.bm25: Optional[BM25Okapi] = None
        self._build_bm25_index()

        # ── Cross-Encoder reranker ──
        reranker_model = os.getenv("RERANKER_MODEL_PATH", "BAAI/bge-reranker-large")
        logger.info("Loading reranker: %s", reranker_model)
        self.rerank_tokenizer = AutoTokenizer.from_pretrained(reranker_model)
        self.rerank_model = AutoModelForSequenceClassification.from_pretrained(reranker_model)
        self.rerank_model.eval()

        logger.info("Hybrid retriever ready — corpus=%d docs, reranker=enabled", len(self.corpus))

    # ── Collection management ──────────────────────────────────────────

    def _ensure_collection(self) -> None:
        """Create collection if not exists, otherwise load it."""
        if self.client.has_collection(self.COLLECTION_NAME):
            self.client.load_collection(self.COLLECTION_NAME)
            logger.info("Milvus collection '%s' loaded", self.COLLECTION_NAME)
            return

        logger.info("Creating Milvus collection '%s' ...", self.COLLECTION_NAME)
        schema = self.client.create_schema(
            auto_id=True,
            enable_dynamic_field=False,
        )
        schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field("text", DataType.VARCHAR, max_length=8192)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=self._embedding_dim)

        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            schema=schema,
        )
        # Create IVF_FLAT index for fast approximate search
        self.client.create_index(
            collection_name=self.COLLECTION_NAME,
            field_name="vector",
            index_params={
                "index_type": "IVF_FLAT",
                "metric_type": "COSINE",
                "params": {"nlist": 128},
            },
        )
        self.client.load_collection(self.COLLECTION_NAME)
        logger.info("Collection '%s' created", self.COLLECTION_NAME)

    def _build_bm25_index(self) -> None:
        """Build BM25 inverted index from all stored documents."""
        try:
            results = self.client.query(
                collection_name=self.COLLECTION_NAME,
                filter="id > 0",
                output_fields=["text"],
                limit=100000,
            )
        except Exception:
            logger.warning("BM25: collection empty or not yet ingested")
            self.corpus = []
            self.bm25 = None
            return

        self.corpus = [r.get("text", "") for r in results] if results else []
        if self.corpus:
            tokenized = [list(doc) for doc in self.corpus]
            self.bm25 = BM25Okapi(tokenized)
            logger.info("BM25 index built: %d docs", len(self.corpus))
        else:
            self.bm25 = None

    # ── Ingestion (called by ingest_docs.py) ──────────────────────────

    def insert(self, chunks: List[str], batch_size: int = 32) -> int:
        """Insert document chunks into Milvus in batches with progress output.

        Returns total count inserted.
        """
        if not chunks:
            return 0

        total = len(chunks)
        total_inserted = 0

        for i in range(0, total, batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size

            print(f"   🔄 Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks) ...")
            embeddings = self.dense_embeddings.embed_documents(batch)
            data = [
                {"text": text, "vector": vec}
                for text, vec in zip(batch, embeddings)
            ]
            result = self.client.insert(collection_name=self.COLLECTION_NAME, data=data)
            inserted = result.get("insert_count", len(batch))
            total_inserted += inserted
            print(f"   ✅ Batch {batch_num}: {inserted} inserted ({total_inserted}/{total} total)")

        # Rebuild BM25 to include new docs
        self._build_bm25_index()
        logger.info("Inserted %d chunks, corpus now %d docs", total_inserted, len(self.corpus))
        return total_inserted

    # ── Dense search ───────────────────────────────────────────────────

    def _dense_search(self, query: str, top_k: int) -> List[str]:
        """Dense vector search via Milvus."""
        try:
            query_vec = self.dense_embeddings.embed_query(query)
            results = self.client.search(
                collection_name=self.COLLECTION_NAME,
                data=[query_vec],
                limit=top_k,
                output_fields=["text"],
            )
            return [hit["entity"]["text"] for hit in results[0]]
        except Exception as exc:
            logger.warning("Dense search failed: %s", exc)
            return []

    # ── Sparse search ──────────────────────────────────────────────────

    def _sparse_search(self, query: str, top_k: int) -> List[str]:
        """BM25 sparse retrieval."""
        if not self.bm25 or not self.corpus:
            return []
        tokenized_query = list(query)
        scores = self.bm25.get_scores(tokenized_query)
        # Get top-k indices
        indices = np.argsort(scores)[::-1][:top_k]
        return [self.corpus[i] for i in indices]

    # ── Fusion ─────────────────────────────────────────────────────────

    @staticmethod
    def _minmax_normalize(scores: List[float]) -> List[float]:
        if not scores:
            return []
        s_min, s_max = min(scores), max(scores)
        if s_max == s_min:
            return [1.0] * len(scores)
        return [(s - s_min) / (s_max - s_min) for s in scores]

    def _rrf_fusion(
        self, dense_results: List[str], sparse_results: List[str], k: int = 60
    ) -> List[str]:
        """Reciprocal Rank Fusion."""
        score_map: dict[str, float] = {}
        for rank, text in enumerate(dense_results):
            score_map[text] = score_map.get(text, 0.0) + 1.0 / (k + rank + 1)
        for rank, text in enumerate(sparse_results):
            score_map[text] = score_map.get(text, 0.0) + 1.0 / (k + rank + 1)

        sorted_items = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        return [text for text, _ in sorted_items]

    def _linear_fusion(
        self, dense_results: List[str], sparse_results: List[str]
    ) -> List[str]:
        """Linear weighted fusion with min-max normalization."""
        # Build unified list preserving order
        all_candidates: list[str] = []
        seen: set[str] = set()
        for t in dense_results + sparse_results:
            if t not in seen:
                all_candidates.append(t)
                seen.add(t)

        dense_scores = {
            t: 1.0 - i / max(len(dense_results), 1)
            for i, t in enumerate(dense_results)
        }
        sparse_scores = {
            t: 1.0 - i / max(len(sparse_results), 1)
            for i, t in enumerate(sparse_results)
        }

        combined: dict[str, float] = {}
        for t in all_candidates:
            ds = dense_scores.get(t, 0.0)
            ss = sparse_scores.get(t, 0.0)
            combined[t] = (
                self.fusion_alpha * ds + (1.0 - self.fusion_alpha) * ss
            )

        sorted_items = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return [text for text, _ in sorted_items]

    # ── Rerank ─────────────────────────────────────────────────────────

    def _cross_encoder_rerank(
        self, query: str, candidates: List[str], top_k: int
    ) -> List[str]:
        """Re-rank candidates with Cross-Encoder."""
        if not candidates:
            return []

        pairs = [[query, doc] for doc in candidates]
        with torch.no_grad():
            inputs = self.rerank_tokenizer(
                pairs, padding=True, truncation=True,
                max_length=512, return_tensors="pt",
            )
            scores = self.rerank_model(**inputs, return_dict=True).logits.squeeze(-1)

        ranked = sorted(
            zip(candidates, scores.tolist()), key=lambda x: x[1], reverse=True
        )
        return [doc for doc, _ in ranked[:top_k]]

    # ── Public API ─────────────────────────────────────────────────────

    def retrieve(self, query: str, top_k: int = FINAL_K) -> List[_Doc]:
        """Run the full hybrid retrieval pipeline, return _Doc list."""
        # Phase 1: parallel dense + sparse retrieval
        dense_results = self._dense_search(query, self.DEFAULT_TOP_K)
        sparse_results = self._sparse_search(query, self.DEFAULT_TOP_K)

        if not dense_results and not sparse_results:
            logger.warning("Both dense and sparse search returned empty")
            return []

        # Phase 2: fusion
        if self.fusion_method == "rrf":
            fused = self._rrf_fusion(dense_results, sparse_results)
        else:
            fused = self._linear_fusion(dense_results, sparse_results)

        # Phase 3: Cross-Encoder rerank
        reranked = self._cross_encoder_rerank(query, fused, top_k)

        logger.info(
            "Hybrid retrieval: dense=%d sparse=%d fused=%d final=%d",
            len(dense_results), len(sparse_results), len(fused), len(reranked),
        )
        return [_Doc(text) for text in reranked]

    def invoke(self, query: str) -> List[_Doc]:
        """LangChain-compatible alias for retrieve()."""
        return self.retrieve(query)

    def get_corpus_size(self) -> int:
        """Return total number of documents in the collection."""
        return len(self.corpus)
