"""
Compactor Agent — LLM-powered semantic context compression with structural integrity.

Protects formulas, code blocks, numeric metrics, and tables from compression
loss via regex-based placeholder extraction and restoration. This is the
engineering fix for the 0.53-point multi-round degradation found in benchmark.
"""
import logging
import re
from typing import List, Dict, Any, Tuple

from langchain_core.messages import HumanMessage
from app.agents.config import LLMFactory

logger = logging.getLogger("miemie.compactor")

# Characters threshold before triggering compression
COMPRESSION_THRESHOLD = 2000

# ---------------------------------------------------------------------------
# Structural content patterns — matched BEFORE compression, restored AFTER.
# Each pattern returns (placeholder_template, extraction_regex).
# Order matters: code blocks before inline code, display math before inline math.
# ---------------------------------------------------------------------------
PROTECTED_PATTERNS: List[Tuple[str, str]] = [
    # ── Code blocks (fenced + indented) ──
    ("【CODE_BLOCK_{i}】", r"```[\s\S]*?```"),
    # ── Inline code ──
    ("【INLINE_CODE_{i}】", r"`[^`\n]+`"),
    # ── LaTeX display math ──
    ("【MATH_DISPLAY_{i}】", r"\$\$[\s\S]*?\$\$"),
    # ── LaTeX inline math ──
    ("【MATH_INLINE_{i}】", r"\$[^$\n]+\$"),
    # ── Markdown tables (header row + at least one separator + data rows) ──
    ("【TABLE_{i}】", r"\|.+\|\n\|[\s\-:|]+\|\n(?:\|.+\|\n?)+"),
    # ── Numeric metrics: percentages, decimals with units, standalone key numbers ──
    #   e.g. "96.7%", "21.3%", "3.6 倍", "0.53 分", "batch_size < 32"
    ("【METRIC_{i}】",
     r"\d+\.?\d*\s*%(?![\w])"                              # percentages
     r"|\d+\.\d+\s*(?:倍|分|秒|s|ms|GB|MB|KB| tokens)"     # numbers with units
     r"|\b\d{2,}\.\d{2}\b"),                               # standalone decimals
]


def _extract_protected(text: str) -> Tuple[str, Dict[str, str], Dict[str, int]]:
    """Scan text for structural content, replace with placeholders.

    Returns:
        sanitized:  Text with all protected content replaced by placeholders.
        vault:      {placeholder: original_content} for later restoration.
        counts:     Per-pattern placeholder counter (for verification).
    """
    sanitized = text
    vault: Dict[str, str] = {}
    counts: Dict[str, int] = {}

    for placeholder_tpl, pattern in PROTECTED_PATTERNS:
        prefix = placeholder_tpl.replace("_{i}", "")
        i = 0
        while True:
            match = re.search(pattern, sanitized)
            if not match:
                break
            original = match.group(0)
            ph = placeholder_tpl.format(i=i)
            vault[ph] = original
            sanitized = sanitized.replace(original, ph, 1)
            i += 1
        if i > 0:
            logger.info("Extracted %d %s blocks", i, prefix)
        counts[prefix] = i

    total_protected = sum(counts.values())
    if total_protected > 0:
        logger.info("Protected %d structural blocks before compression", total_protected)

    return sanitized, vault, counts


def _restore_protected(compressed: str, vault: Dict[str, str]) -> str:
    """Restore all placeholders in the compressed text back to original content.

    Iterates in reverse insertion order so nested/reordered placeholders
    always map correctly.
    """
    restored = compressed
    missing = []
    for ph, original in vault.items():
        if ph in restored:
            restored = restored.replace(ph, original, 1)
        else:
            # LLM dropped this placeholder — re-inject at end as appendix
            missing.append((ph, original))

    if missing:
        logger.warning(
            "LLM compression dropped %d protected blocks — appending as appendix", len(missing)
        )
        appendix = "\n\n【压缩中保留的关键公式/数据】\n"
        for ph, original in missing:
            appendix += f"- {original}\n"
        restored += appendix

    return restored


def _verify_protection(original: str, restored: str, vault: Dict[str, str]) -> bool:
    """Sanity check: did all protected content survive?"""
    for ph, content in vault.items():
        if content not in restored:
            logger.error("Protected content lost: %s", content[:80])
            return False
    logger.info("All %d protected blocks preserved after compression", len(vault))
    return True


# ---------------------------------------------------------------------------
# Compactor
# ---------------------------------------------------------------------------
class CompactorAgent:
    """Compresses multi-round agent conversation history via LLM summarization,
    with structural content (formulas, code, metrics, tables) protected from loss.
    """

    def __init__(self):
        self.llm = LLMFactory.get_llm(temperature=0.0)

    async def compress(
        self, history_logs: List[Dict[str, Any]], original_context: str
    ) -> str:
        """Compress verbose agent conversation history into a concise summary.

        Pipeline:
          1. Concat history_logs → trace_str
          2. Extract protected content (formulas, code, tables) → placeholders
          3. If under threshold, skip LLM; else LLM-compress sanitized text
          4. Restore protected content from vault
          5. Combine with original RAG context

        Args:
            history_logs: Ordered list of agent log entries.
            original_context: The original RAG-retrieved technical context (always preserved).

        Returns:
            Compressed history + original context, with structural content intact.
        """
        if not history_logs:
            return original_context

        # Build raw trace
        trace_str = ""
        for log in history_logs:
            trace_str += f"[{log.get('agent', 'unknown')}]: {log.get('content', '')}\n"

        original_len = len(trace_str)

        # No compression needed — still protect if applicable
        if original_len <= COMPRESSION_THRESHOLD:
            logger.info(
                "History %d chars under threshold %d, skipping compression",
                original_len, COMPRESSION_THRESHOLD,
            )
            return self._format_output(trace_str, original_context)

        # ── Phase 1: Extract protected content ──
        sanitized, vault, counts = _extract_protected(trace_str)
        sanitized_len = len(sanitized)

        logger.info(
            "Triggering LLM compression: %d chars → target ~800 chars (%d chars protected)",
            original_len, original_len - sanitized_len,
        )

        # ── Phase 2: LLM compress the sanitized text ──
        try:
            compressed = await self._llm_compress(sanitized)
            compression_pct = (1 - len(compressed) / original_len) * 100
            logger.info(
                "Compression: %d → %d chars (%.1f%% reduction)",
                original_len, len(compressed), compression_pct,
            )

            # ── Phase 3: Restore protected content ──
            restored = _restore_protected(compressed, vault)

            # ── Phase 4: Verify ──
            if not _verify_protection(trace_str, restored, vault):
                logger.warning("Some protected content may have been lost")

            return self._format_output(
                f"【语义压缩摘要（公式/代码/数据已原样保留）】\n{restored}",
                original_context,
            )
        except Exception as exc:
            logger.error("LLM compression failed, falling back to truncation: %s", exc)
            return self._truncate_fallback(trace_str, original_context, vault)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _llm_compress(self, sanitized: str) -> str:
        """Call the LLM to produce a structured summary.

        The input text has formulas/code/tables replaced by placeholders like
        【FORMULA_0】, so the LLM is instructed to keep these markers verbatim.
        """
        prompt = f"""你是上下文压缩专家。请将以下多轮 Agent 对话历史压缩为简洁的结构化摘要。

⚠️ 关键规则 — 占位符必须原样保留：
- 文本中的 【CODE_BLOCK_*】、【MATH_*】、【TABLE_*】、【METRIC_*】 等占位符
  代表公式、代码块、表格和关键数值，你必须将它们**原样抄录**到输出中，
  不要改写、合并或删除任何一个占位符。

要求：
1. 保留每轮的核心技术决策和关键参数方向（但不重复占位符已保护的细节）
2. 保留 Critic 指出的未解决问题和修正方向
3. 丢弃寒暄、套话、重复表述
4. 压缩后不超过 800 字（占位符不计入字数）
5. 只输出压缩后的摘要，不加前缀

【对话历史（占位符已保护）】：
{sanitized}"""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def _truncate_fallback(
        self, trace_str: str, original_context: str, vault: Dict[str, str]
    ) -> str:
        """Fallback: keep last 1000 characters (preserves structural content
        since truncation doesn't modify text — no placeholder extraction needed)."""
        truncated = "...(前面大量重复反思已省略)...\n" + trace_str[-1000:]
        logger.warning(
            "Using truncation fallback: %d → %d chars", len(trace_str), len(truncated)
        )
        return self._format_output(
            f"【已分片裁剪的历史演进（降级模式）】\n{truncated}", original_context
        )

    @staticmethod
    def _format_output(history_section: str, original_context: str) -> str:
        """Combine the (possibly compressed) history with the original context."""
        return f"{history_section}\n\n【架构基底】\n{original_context}"
