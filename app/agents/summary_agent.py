"""
Summary Agent — final report formatting and business-friendly translation.

Converts the raw architectural analysis into a polished, structured Markdown
report suitable for presentation to non-technical stakeholders.
"""
import logging

from langchain_core.messages import HumanMessage
from app.graph.state import GraphState
from app.agents.config import LLMFactory

logger = logging.getLogger("miemie.summary")


class SummaryAgent:
    def __init__(self):
        self.llm = LLMFactory.get_llm(temperature=0.1)

    async def run(self, state: GraphState) -> dict:
        logger.info("SummaryAgent generating final report...")

        query = state.get("query", "")
        analysis_res = state.get("analyzer_output", {}).get("analysis", "未提取到有效分析")

        prompt = f"""你是一位资深的 AI 产品架构总监。请将下方技术团队提供的【硬核推演报告】，转换为一份格式优美、业务方易读的【最终技术审计报告】。

【原始痛点需求】：{query}
【硬核推演报告】：{analysis_res}

【严苛排版要求】：
1. 必须是一篇结构完整的 Markdown 文章。
2. 开头必须有一个醒目的一级标题（如：# 🛠️ AI Infra 架构审计报告）。
3. 请提炼出 3-4 个二级标题（##）。
4. 大量使用列表（- **加粗核心词**：具体解释）来罗列架构亮点和风险点。
5. 语气要极其专业、笃定，体现大厂架构师的压迫感。"""

        try:
            res = await self.llm.ainvoke([HumanMessage(content=prompt)])
            final_report = res.content

            logger.info(
                "SummaryAgent complete — final report: %d chars", len(final_report)
            )

            new_log = {
                "agent": "Summary Agent",
                "content": "已完成核心架构报告的业务降维与 Markdown 排版。全链路流转圆满结束。",
            }

            return {
                "summary_output": {"status": "completed"},
                "final_report": final_report,
                "history_logs": state.get("history_logs", []) + [new_log],
            }

        except Exception as e:
            logger.error("SummaryAgent generation failed: %s", e)
            return {
                "summary_output": {"status": "error"},
                "final_report": f"报告生成异常：{str(e)}",
                "history_logs": state.get("history_logs", [])
                + [{"agent": "Summary Agent", "content": f"排版失败: {str(e)}"}],
            }
