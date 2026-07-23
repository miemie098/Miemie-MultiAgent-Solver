"""
Unit tests for CompactorAgent — tests both LLM compression and truncation fallback.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.compactor_agent import CompactorAgent


class TestCompactorAgent:
    """Tests for CompactorAgent.compress()"""

    def test_short_history_skips_compression(self):
        """History under threshold should be returned unchanged (no LLM call)."""
        compactor = CompactorAgent()
        short_history = [
            {"agent": "Analyzer", "content": "Short analysis."},
        ]
        original = "Core architecture context."

        import asyncio
        result = asyncio.run(compactor.compress(short_history, original))

        assert "Short analysis" in result
        assert "Core architecture context" in result
        assert "语义压缩摘要" not in result

    def test_empty_history_returns_original_context(self):
        """Empty history should return original context unchanged."""
        compactor = CompactorAgent()
        import asyncio
        result = asyncio.run(compactor.compress([], "Original context only"))
        assert result == "Original context only"

    @pytest.mark.asyncio
    async def test_long_history_triggers_compression(self):
        """History exceeding threshold should trigger LLM compression."""
        compactor = CompactorAgent()

        # Replace the LLM with a mock
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Compressed summary of the history."
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        compactor.llm = mock_llm

        long_history = [
            {"agent": "Analyzer", "content": "X" * 1500},
            {"agent": "Critic", "content": "Y" * 1500},
        ]

        result = await compactor.compress(long_history, "Original context")

        assert "Compressed summary" in result
        assert "Original context" in result
        mock_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_llm_failure_falls_back_to_truncation(self):
        """When LLM call fails, should fall back to string truncation."""
        compactor = CompactorAgent()

        # Replace the LLM with a mock that raises
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API error"))
        compactor.llm = mock_llm

        long_history = [
            {"agent": "Analyzer", "content": "A" * 1500},
            {"agent": "Critic", "content": "B" * 1500},
        ]

        result = await compactor.compress(long_history, "Original context")

        # Should fall back to truncation
        assert "降级模式" in result
        assert "Original context" in result

    # ── Structural content protection tests ──

    @pytest.mark.asyncio
    async def test_protects_latex_formula(self):
        """LaTeX formulas should survive compression via placeholder protection."""
        compactor = CompactorAgent()

        mock_llm = MagicMock()
        # LLM returns compressed text with the placeholder still present
        mock_response = MagicMock()
        mock_response.content = "压缩结果中提到公式 【MATH_INLINE_0】 是关键。"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        compactor.llm = mock_llm

        long_history = [
            {"agent": "Analyzer",
             "content": "测试内容。" + "X" * 1000},
            {"agent": "Critic",
             "content": "KV Cache 碎片率公式为 $f = 1 - (\\sum b_i / B_{max})$，" + "Y" * 1000},
        ]

        result = await compactor.compress(long_history, "Original context")

        # The formula should be in the output
        assert "f = 1 - (\\sum b_i / B_{max})" in result
        assert "MATH_INLINE_0" not in result  # placeholder should be restored

    @pytest.mark.asyncio
    async def test_protects_code_block(self):
        """Code blocks should survive compression."""
        compactor = CompactorAgent()

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "包含一个代码块 【CODE_BLOCK_0】 定义了关键逻辑。"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        compactor.llm = mock_llm

        code_snippet = """```python
def allocate_kv_cache(batch_size: int) -> int:
    return batch_size * 4096
```"""
        long_history = [
            {"agent": "Analyzer", "content": "X" * 1000 + code_snippet + "X" * 1000},
            {"agent": "Critic", "content": "Y" * 1000},
        ]

        result = await compactor.compress(long_history, "Original context")

        assert "def allocate_kv_cache" in result
        assert "batch_size * 4096" in result
        assert "CODE_BLOCK_0" not in result

    @pytest.mark.asyncio
    async def test_protects_percentage_metric(self):
        """Numeric percentages should be protected as METRIC placeholders."""
        compactor = CompactorAgent()

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "利用率从 【METRIC_0】 提升至 【METRIC_1】。"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        compactor.llm = mock_llm

        long_history = [
            {"agent": "Analyzer",
             "content": "内存利用率从 21.3% 提升至 96.7%。" + "X" * 1000},
            {"agent": "Critic", "content": "Y" * 1000},
        ]

        result = await compactor.compress(long_history, "Original context")

        assert "21.3%" in result
        assert "96.7%" in result
        assert "METRIC_0" not in result
        assert "METRIC_1" not in result

    @pytest.mark.asyncio
    async def test_llm_drops_placeholder_appends_appendix(self):
        """If LLM drops a placeholder, it should be re-injected as appendix."""
        compactor = CompactorAgent()

        mock_llm = MagicMock()
        mock_response = MagicMock()
        # LLM drops the MATH_INLINE_0 placeholder
        mock_response.content = "压缩结果中省略了公式部分。"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        compactor.llm = mock_llm

        long_history = [
            {"agent": "Analyzer",
             "content": "误差公式 $E = mc^2$ 是核心。" + "X" * 1000},
            {"agent": "Critic", "content": "Y" * 1000},
        ]

        result = await compactor.compress(long_history, "Original context")

        # Formula should appear in the appendix
        assert "E = mc^2" in result
        assert "压缩中保留的关键公式" in result
