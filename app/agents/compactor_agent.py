"""
Compactor Agent — LLM-powered semantic context compression.

Replaces naive string truncation with structured summarization that preserves
key architectural decisions, unresolved critic concerns, and correction directions
while discarding verbose boilerplate from multi-round reflection loops.
"""
import logging
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage
from app.agents.config import LLMFactory

logger = logging.getLogger("miemie.compactor")

# Characters threshold before triggering compression
COMPRESSION_THRESHOLD = 2000


class CompactorAgent:
    """Compresses multi-round agent conversation history via LLM summarization.

    Falls back to simple truncation if the LLM call fails, ensuring the
    workflow never breaks due to compression errors.
    """

    def __init__(self):
        self.llm = LLMFactory.get_llm(temperature=0.0)

    async def compress(
        self, history_logs: List[Dict[str, Any]], original_context: str
    ) -> str:
        """
        Compress verbose agent conversation history into a concise summary.

        Args:
            history_logs: Ordered list of agent log entries (agent name + content).
            original_context: The original RAG-retrieved technical context (preserved).

        Returns:
            A string combining the compressed history and original context.
        """
        if not history_logs:
            return original_context

        # Build the raw trace string
        trace_str = ""
        for log in history_logs:
            trace_str += f"[{log.get('agent', 'unknown')}]: {log.get('content', '')}\n"

        original_len = len(trace_str)

        # Skip compression for short histories
        if original_len <= COMPRESSION_THRESHOLD:
            logger.info(
                "History length %d chars under threshold %d, skipping compression",
                original_len, COMPRESSION_THRESHOLD,
            )
            return self._format_output(trace_str, original_context)

        logger.info(
            "Triggering LLM compression: %d chars → target ~800 chars", original_len
        )

        # Attempt LLM-powered semantic compression
        try:
            compressed = await self._llm_compress(trace_str)
            compression_pct = (1 - len(compressed) / original_len) * 100
            logger.info(
                "Compression complete: %d → %d chars (%.1f%% reduction)",
                original_len, len(compressed), compression_pct,
            )
            return self._format_output(
                f"【语义压缩摘要】\n{compressed}", original_context
            )
        except Exception as exc:
            logger.error("LLM compression failed, falling back to truncation: %s", exc)
            return self._truncate_fallback(trace_str, original_context, original_len)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _llm_compress(self, trace_str: str) -> str:
        """Call the LLM to produce a structured summary of the history."""
        prompt = f"""你是一个上下文压缩专家。请将以下多轮Agent对话历史压缩为简洁的结构化摘要。

要求：
1. 保留每一轮的核心技术决策和关键参数
2. 保留 Critic 指出的未解决问题和修正方向
3. 丢弃寒暄、套话、重复表述
4. 压缩后不超过 800 字
5. 只输出压缩后的摘要，不要加任何前缀说明

【对话历史】：
{trace_str}"""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def _truncate_fallback(
        self, trace_str: str, original_context: str, original_len: int
    ) -> str:
        """Fallback: keep the last 1000 characters with a truncation marker."""
        truncated = "...(前面大量重复反思已省略)...\n" + trace_str[-1000:]
        logger.warning(
            "Using truncation fallback: %d → %d chars", original_len, len(truncated)
        )
        return self._format_output(
            f"【已分片裁剪的历史演进（降级模式）】\n{truncated}", original_context
        )

    @staticmethod
    def _format_output(history_section: str, original_context: str) -> str:
        """Combine the (possibly compressed) history with the original context."""
        return f"{history_section}\n\n【架构基底】\n{original_context}"
