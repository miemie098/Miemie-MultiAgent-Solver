"""
Moderator Agent — synthesizes multi-critic debate results into a unified verdict.

Uses majority voting with confidence weighting to decide whether the analysis
passes review or requires another iteration.
"""
import logging
from typing import Dict, List

from langchain_core.messages import HumanMessage
from app.agents.config import LLMFactory

logger = logging.getLogger("miemie.moderator")

# Consensus threshold: need at least this fraction of HEALTHY critics to pass
PASS_RATIO = 2 / 3  # ≥ 2 out of 3 healthy critics must approve

# Average confidence must exceed this for a pass (degraded votes excluded)
MIN_AVG_CONFIDENCE = 0.6


class ModeratorAgent:
    """Synthesizes multiple critic verdicts into a single go/no-go decision.

    Algorithm:
      1. Separate healthy critics from degraded (abstention) verdicts.
      2. Count pass votes among healthy critics only.
      3. Compute average confidence from healthy critics only.
      4. If healthy >= 2 and pass_ratio >= 2/3 and avg_confidence >= 0.6 → pass.
      5. Otherwise → fail, and produce unified improvement feedback via LLM.

    Degraded critics (e.g. DeepSeek API unreachable after 3 retries) are
    explicitly excluded from the quorum to prevent false negatives.
    """

    def __init__(self):
        self.llm = LLMFactory.get_llm(temperature=0.1)

    async def synthesize(
        self, query: str, analysis: str, critiques: List[Dict]
    ) -> Dict:
        """
        Args:
            query: The original user question.
            analysis: The Analyzer's output being reviewed.
            critiques: List of dicts from each critic persona.
                       May contain 'degraded': True entries (abstentions).

        Returns:
            {"consensus": bool, "feedback": str, "confidence": float, "details": ...}
        """
        healthy = [c for c in critiques if not c.get("degraded")]
        degraded = [c for c in critiques if c.get("degraded")]

        if not healthy:
            # All degraded — caller should have escalated before reaching here
            logger.error("Moderator: 0 healthy critics — cannot form quorum")
            return {
                "consensus": False,
                "feedback": "所有审查节点不可用，无法形成有效决议。请检查 API 服务后重试。",
                "confidence": 0.0,
                "details": {
                    "votes_passed": 0,
                    "total_critics": len(critiques),
                    "healthy": 0,
                    "degraded": len(degraded),
                    "avg_confidence": 0.0,
                },
            }

        passed_count = sum(1 for c in healthy if c.get("passed", False))
        avg_confidence = (
            sum(c.get("confidence", 0.5) for c in healthy) / len(healthy)
        )

        # Dynamic threshold: need ≥ ceil(healthy * PASS_RATIO) pass votes
        required = max(2, int(len(healthy) * PASS_RATIO + 0.5))

        logger.info(
            "Moderator: %d/%d healthy passed (need %d), avg_confidence=%.2f, degraded=%d",
            passed_count, len(healthy), required, avg_confidence, len(degraded),
        )

        passed = passed_count >= required and avg_confidence >= MIN_AVG_CONFIDENCE

        if passed:
            logger.info("Moderator: CONSENSUS — analysis approved")
            feedback = self._build_pass_feedback(healthy)
            if degraded:
                feedback += f"（注意：{len(degraded)} 个审查节点因服务不可用弃权）"
        else:
            logger.info("Moderator: REJECTED — synthesizing unified feedback")
            feedback = await self._synthesize_feedback(query, analysis, healthy)
            if degraded:
                feedback += f"\n\n[系统提示] {len(degraded)} 个审查节点因服务不可用弃权，本决议仅基于 {len(healthy)} 个有效投票。"

        return {
            "consensus": passed,
            "feedback": feedback,
            "confidence": avg_confidence,
            "details": {
                "votes_passed": passed_count,
                "total_critics": len(critiques),
                "healthy": len(healthy),
                "degraded": len(degraded),
                "required_votes": required,
                "avg_confidence": avg_confidence,
            },
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    async def _synthesize_feedback(
        self, query: str, analysis: str, critiques: List[Dict]
    ) -> str:
        """Ask the LLM to merge multiple critiques into one coherent revision plan."""
        critique_text = ""
        for i, c in enumerate(critiques):
            persona = ["乐观审查员", "悲观审查员", "务实审查员"][i] if i < 3 else f"审查员{i+1}"
            concerns = c.get("key_concerns", [])
            fix = c.get("suggested_fix", "无")
            critique_text += (
                f"\n### {persona}\n"
                f"- 通过: {c.get('passed', False)}\n"
                f"- 信心度: {c.get('confidence', 0):.2f}\n"
                f"- 主要关切: {', '.join(concerns) if concerns else '无'}\n"
                f"- 修正建议: {fix}\n"
            )

        prompt = f"""你是一个多智能体辩论主持人。以下是 3 位不同视角的审查员对同一份技术报告的评审意见：

{critique_text}

【原始任务】：{query}

请综合三方意见，给出一份**统一的修正方案**（不超过 500 字），明确指出 Analyzer 应该：
1. 优先修复哪些关键问题
2. 保留哪些被认可的亮点
3. 具体的修改方向"""

        try:
            res = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return res.content.strip()
        except Exception as exc:
            logger.error("Moderator feedback synthesis failed: %s", exc)
            # Fallback: concatenate raw suggestions
            fallback = "\n".join(
                c.get("suggested_fix", "") for c in critiques if c.get("suggested_fix")
            )
            return fallback or "综合三方意见，建议对分析报告进行全面修订。"

    @staticmethod
    def _build_pass_feedback(critiques: List[Dict]) -> str:
        """Build a concise pass summary from all critics."""
        concerns = []
        for c in critiques:
            concerns.extend(c.get("key_concerns", []))
        if concerns:
            return f"多方评审通过。需注意的小问题：{'；'.join(concerns[:3])}"
        return "三方审查员一致通过，分析方案成熟可靠。"
