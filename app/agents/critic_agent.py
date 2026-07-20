"""
Critic Agent — rigorous robustness review with structured JSON output.

Temperature is forced to 0.0 for deterministic, consistent pass/fail judgments.
"""
import json
import logging
import re
import traceback

from langchain_core.messages import HumanMessage
from app.graph.state import GraphState
from app.agents.config import LLMFactory

logger = logging.getLogger("miemie.critic")


class CriticAgent:
    def __init__(self):
        self.llm = LLMFactory.get_llm(temperature=0.0)

    async def run(self, state: GraphState) -> dict:
        logger.info("CriticAgent starting robustness review...")

        query = state.get("query", "")
        analyzer_res = state.get("analyzer_output", {}).get("analysis", "")
        current_count = state.get("correction_count", 0)

        prompt = f"""你是一位极其严苛的 AI Infra 架构审查员。请对以下生成的【架构分析报告】进行严格的鲁棒性审查。

【原始任务】：{query}

【待审查报告】：
{analyzer_res}

【审查准则】：
1. 检查报告中是否存在高并发死锁、内存泄漏或逻辑漏洞。
2. 检查报告是否偏离了原始任务。
3. 如果完全合格且没有硬伤，判定为通过；如果有任何缺陷，判定为拒绝，并给出具体的修正建议。

【输出格式】（至关重要）：
请严格按照以下 JSON 格式输出，不要包含任何 Markdown 符号或其他废话：
{{"passed": true或false, "feedback": "你的详细审查意见"}}"""

        try:
            res = await self.llm.ainvoke([HumanMessage(content=prompt)])
            content = res.content

            # Defensive JSON parsing — model may wrap in markdown or add prose
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                result_data = json.loads(match.group())
                passed = result_data.get("passed", False)
                feedback = result_data.get("feedback", "无详细审查意见")
            else:
                passed = False
                feedback = f"解析大模型审查结果失败，强制触发重试。原始输出：{content[:100]}..."

            status_text = "通过" if passed else "拒绝"
            logger.info(
                "CriticAgent verdict: %s (round %d/%d)",
                status_text, current_count + 1, state.get("max_corrections", "?"),
            )

            new_log = {"agent": "Critic Agent", "content": f"【{status_text}】 {feedback}"}

            return {
                "critic_output": {"passed": passed, "feedback": feedback},
                "history_logs": state.get("history_logs", []) + [new_log],
                "correction_count": current_count + 1,
            }

        except Exception as e:
            logger.error("CriticAgent LLM call failed: %s", e)
            traceback.print_exc()
            error_msg = f"大模型审查异常: {str(e)}"
            return {
                "critic_output": {"passed": False, "feedback": error_msg},
                "history_logs": state.get("history_logs", [])
                + [{"agent": "Critic Agent", "content": f"【异常】{error_msg}"}],
                "correction_count": current_count + 1,
            }
