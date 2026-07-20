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
