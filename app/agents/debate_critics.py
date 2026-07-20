"""
Debate Critics — three distinct reviewer personas for multi-perspective code review.

Each critic evaluates the same analysis from a different philosophical standpoint,
enabling the Moderator to reach a more robust consensus than a single reviewer.
"""
import json
import logging
import re
from typing import Dict

from langchain_core.messages import HumanMessage
from app.agents.config import LLMFactory

logger = logging.getLogger("miemie.debate")


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------
class BaseCriticPersona:
    """Shared logic for all critic personas. Subclasses override PERSONA_PROMPT."""

    PERSONA_PROMPT: str = ""

    def __init__(self):
        self.llm = LLMFactory.get_llm(temperature=0.0)

    async def critique(self, query: str, analysis: str) -> Dict:
        """Evaluate the analysis and return a structured verdict."""
        persona_name = self.__class__.__name__
        logger.info("%s starting review...", persona_name)

        prompt = f"""{self.PERSONA_PROMPT}

【原始任务】：{query}

【待审查报告】：
{analysis}

请严格按照 JSON 格式输出（不要包含任何 Markdown 或额外文字）：
{{"passed": true或false, "confidence": 0.0到1.0之间的数值, "key_concerns": ["问题1", "问题2"], "suggested_fix": "你的修正建议"}}"""

        try:
            res = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return self._parse_response(res.content)
        except Exception as exc:
            logger.error("%s failed: %s", persona_name, exc)
            return {
                "passed": False,
                "confidence": 0.0,
                "key_concerns": [f"Critic evaluation error: {str(exc)}"],
                "suggested_fix": "请重新分析。",
            }

    def _parse_response(self, content: str) -> Dict:
        """Defensively parse JSON from LLM output."""
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {
            "passed": False,
            "confidence": 0.0,
            "key_concerns": ["Failed to parse critic output."],
            "suggested_fix": "请重新输出合法的 JSON 格式。",
        }


# ---------------------------------------------------------------------------
# Three distinct critic personas
# ---------------------------------------------------------------------------
class OptimistCritic(BaseCriticPersona):
    PERSONA_PROMPT = """你是一个**乐观的**架构审查员。你倾向于认可创新方案的价值，相信工程师能找到可行的实现路径。

审查时请关注：
1. 方案是否具备创新性和前瞻性？
2. 核心思路是否合理，即使细节有待完善？
3. 如果存在小问题，是否可以通过工程实践解决？

请给出你的判断。"""


class SkepticCritic(BaseCriticPersona):
    PERSONA_PROMPT = """你是一个**极度悲观的**架构审查员。你假设所有方案都有隐藏的致命缺陷，你的职责是在灾难发生前找出它们。

审查时请关注：
1. 高并发场景下是否存在死锁、竞态条件或内存泄漏？
2. 单点故障在哪里？容错机制是否充分？
3. 是否存在理论上的不可能性（如 CAP 定理冲突）？

请给出你的判断。"""


class RealistCritic(BaseCriticPersona):
    PERSONA_PROMPT = """你是一个**务实的**架构审查员。你平衡评估方案的利弊，既不盲目乐观也不过度悲观。

审查时请关注：
1. 方案在现有技术栈下是否可实现？
2. 性能/成本/复杂度的 trade-off 是否合理？
3. 与业界最佳实践（如 vLLM、SGLang 等）相比是否有竞争力？

请给出你的判断。"""
