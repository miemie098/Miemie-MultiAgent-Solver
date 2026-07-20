import re
import os
import sys
import json
import asyncio

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage
from app.agents.config import LLMFactory
from app.graph.workflow import create_workflow


async def evaluate_output(task: str, response: str, context: str) -> dict:
    judge_llm = LLMFactory.get_llm(temperature=0.0)
    prompt = f"""
    作为AI架构专家，请基于【事实锚点】评测架构设计案：
    【任务】：{task}
    【事实锚点】：{context}
    【待评测回答】：{response}

    评分维度（0-10）：
    1. Faithfulness (忠实度)：回答是否严格基于锚点事实？
    2. Relevance (相关性)：是否解决了架构痛点？

    请强制返回严格的 JSON 对象（不要包含任何其他字符）：
    {{"faithfulness": 0, "relevance": 0, "comment": "详细评语"}}
    """
    res = await judge_llm.ainvoke([HumanMessage(content=prompt)])
    try:
        # 匹配大括号中的 JSON 内容
        match = re.search(r'\{.*\}', res.content, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("未能找到 JSON 结构")
    except Exception as e:
        return {"faithfulness": 0, "relevance": 0, "comment": f"解析失败: 原始大模型输出为 -> {res.content[:50]}"}


async def run_production_eval():
    print("====== 🚀 启动大厂级【深度判别式评测大盘】 ======\n")
    app_graph = create_workflow()

    # 💡 优化了测试用例：尽量提问和你灌入数据库的论文强相关的题目
    for task in [
        "设计 10 万并发架构，要求考虑高可用、Redis 缓存穿透以及分布式锁的设计方案",
        "分析 DeepSeek-V3 MLA 机制",
        "比较 PagedAttention 和 vLLM 的显存优化差异",
        "在处理极长文本时，目前的注意力机制存在哪些显存瓶颈？"
    ]:
        print(f"\n▶️ 正在推演任务: {task}")
        # 初始化状态（不再传入写死的 paper_context）
        initial_state = {
            "query": task, "paper_context": "", "max_corrections": 3,
            "correction_count": 0, "history_logs": []
        }

        # 执行图流转
        agent_res = await app_graph.ainvoke(initial_state)
        report = agent_res.get("final_report", "")

        # 🌟 核心修复：提取 SearchAgent 真正检索到的内容，作为裁判的评判标准！
        real_retrieved_context = agent_res.get("search_output", {}).get("context", "无搜索上下文")

        # 开始打分
        eval_res = await evaluate_output(task, report, real_retrieved_context)
        print(f"✅ 忠实度: {eval_res.get('faithfulness', 0)}/10 | 相关性: {eval_res.get('relevance', 0)}/10")
        print(f"📝 裁判评语: {eval_res.get('comment', '无')}")
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(run_production_eval())