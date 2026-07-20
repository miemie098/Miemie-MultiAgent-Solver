"""
Analyzer Agent — deep architectural analysis via LLM.

Temperature is set to 0.3 to allow some creative divergence in analysis
while maintaining technical rigor.
"""
import logging
import traceback

from langchain_core.messages import HumanMessage
from app.graph.state import GraphState
from app.agents.config import LLMFactory

logger = logging.getLogger("miemie.analyzer")


class AnalyzerAgent:
    def __init__(self):
        self.llm = LLMFactory.get_llm(temperature=0.3)

    async def run(self, state: GraphState) -> dict:
        logger.info("AnalyzerAgent starting deep analysis...")

        query = state.get("query", "")
        # Prefer compressed context from prior loop iterations; fall back to original
        context = state.get("compressed_context") or state.get("paper_context", "无可用上下文")

        prompt = f"""你是一个资深的 AI Infra 架构专家。请基于以下【参考上下文】，对【主任务】进行深度的技术分析与架构推演。

【主任务】：{query}

【参考上下文】：
{context}

【输出要求】：
请直接输出专业、硬核的架构推演报告，包含核心痛点、技术拓扑设计及潜在瓶颈分析。拒绝废话和寒暄。"""

        try:
            res = await self.llm.ainvoke([HumanMessage(content=prompt)])
            analysis_res = res.content

            logger.info(
                "AnalyzerAgent complete — %d chars generated", len(analysis_res)
            )

            new_log = {
                "agent": "Analyzer Agent",
                "content": f"已完成深度推演，生成了 {len(analysis_res)} 字符的架构报告。",
            }
            return {
                "analyzer_output": {"analysis": analysis_res, "status": "completed"},
                "history_logs": state.get("history_logs", []) + [new_log],
            }

        except Exception as e:
            logger.error("AnalyzerAgent LLM call failed: %s", e)
            traceback.print_exc()
            error_msg = f"大模型调用失败: {str(e)}"
            return {
                "analyzer_output": {"analysis": error_msg, "status": "error"},
                "history_logs": state.get("history_logs", [])
                + [{"agent": "Analyzer Agent", "content": error_msg}],
            }
