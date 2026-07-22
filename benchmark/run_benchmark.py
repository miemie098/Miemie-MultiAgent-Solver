#!/usr/bin/env python
"""
Automated benchmark — compares 4 solver modes across 10+ test cases.

Modes:
  1. baseline_single : Single Analyzer, no Critic, no reflection
  2. single_critic   : Analyzer → Critic → 1 round only
  3. multi_round     : Full reflective loop (current default)
  4. debate          : 3-critic parallel debate mode

Metrics (via LLM-as-judge):
  - faithfulness  (0-10): How well does the answer stick to verified facts?
  - relevance     (0-10): How well does it address the original question?
  - coherence     (0-10): Is the answer well-structured and logical?

Usage:
  python benchmark/run_benchmark.py              # all modes, all cases
  DEBATE_MODE=debate python benchmark/run_benchmark.py  # debate comparison
"""
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Project root
BENCHMARK_DIR = Path(__file__).parent
PROJECT_ROOT = BENCHMARK_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.messages import HumanMessage
from app.agents.config import LLMFactory
from app.graph.workflow import create_workflow

logging.basicConfig(
    level=logging.WARNING,  # suppress INFO noise during benchmark
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger("benchmark")
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Judge
# ---------------------------------------------------------------------------
async def evaluate_output(task: str, response: str) -> dict:
    """LLM-as-judge: score an answer on faithfulness, relevance, coherence."""
    judge_llm = LLMFactory.get_llm(temperature=0.0)

    prompt = f"""作为 AI 架构评估专家，请对以下回答评分（0-10 整数）：

【任务】：{task}
【待评回答】：{response}

评分维度：
1. faithfulness (忠实度)：回答是否基于合理的技术事实，无明显编造？
2. relevance (相关性)：是否直接解决了问题？
3. coherence (连贯性)：结构是否清晰，逻辑是否自洽？

请严格返回 JSON：{{"faithfulness": 0, "relevance": 0, "coherence": 0, "comment": "评语"}}"""

    try:
        res = await judge_llm.ainvoke([HumanMessage(content=prompt)])
        match = re.search(r"\{.*\}", res.content, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return {"faithfulness": 0, "relevance": 0, "coherence": 0, "comment": "评分解析失败"}


# ---------------------------------------------------------------------------
# Mode runners
# ---------------------------------------------------------------------------
async def run_baseline_single(query: str) -> tuple:
    """Single Analyzer, no Critic — simplest baseline."""
    from app.agents.analyzer_agent import AnalyzerAgent
    from app.agents.summary_agent import SummaryAgent

    state = {
        "query": query,
        "paper_context": "",
        "compressed_context": "",
        "history_logs": [],
    }

    start = time.time()
    analyzer = AnalyzerAgent()
    result = await analyzer.run(state)
    summary = SummaryAgent()
    final = await summary.run({**state, **result})
    elapsed = time.time() - start

    return final.get("final_report", ""), elapsed, 1


async def run_single_critic(query: str) -> tuple:
    """Analyzer → Critic (1 round only)."""
    from app.graph.workflow import create_workflow
    import os as _os
    _os.environ["DEBATE_MODE"] = "single"

    workflow = create_workflow()
    initial_state = _make_state(query, max_corrections=1)

    start = time.time()
    final = await workflow.ainvoke(initial_state)
    elapsed = time.time() - start

    _os.environ["DEBATE_MODE"] = "single"
    return final.get("final_report", ""), elapsed, final.get("correction_count", 1)


async def run_multi_round(query: str) -> tuple:
    """Full multi-round reflective loop."""
    from app.graph.workflow import create_workflow
    import os as _os
    _os.environ["DEBATE_MODE"] = "single"

    workflow = create_workflow()
    initial_state = _make_state(query, max_corrections=3)

    start = time.time()
    final = await workflow.ainvoke(initial_state)
    elapsed = time.time() - start

    _os.environ["DEBATE_MODE"] = "single"
    return final.get("final_report", ""), elapsed, final.get("correction_count", 1)


async def run_debate(query: str) -> tuple:
    """3-critic debate mode."""
    from app.graph.workflow import create_workflow
    import os as _os
    _os.environ["DEBATE_MODE"] = "debate"

    workflow = create_workflow()
    initial_state = _make_state(query, max_corrections=3)

    start = time.time()
    final = await workflow.ainvoke(initial_state)
    elapsed = time.time() - start

    _os.environ["DEBATE_MODE"] = "single"
    return final.get("final_report", ""), elapsed, final.get("correction_count", 1)


def _make_state(query: str, max_corrections: int) -> dict:
    return {
        "query": query,
        "paper_context": "",
        "max_corrections": max_corrections,
        "correction_count": 0,
        "history_logs": [],
        "search_output": {},
        "analyzer_output": {},
        "critic_output": {},
        "compactor_output": {},
        "summary_output": {},
        "compressed_context": "",
        "final_report": "",
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main():
    with open(BENCHMARK_DIR / "test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    logger.info("Benchmark: %d test cases × 4 modes", len(test_cases))

    modes = [
        ("baseline_single", run_baseline_single),
        ("single_critic", run_single_critic),
        ("multi_round", run_multi_round),
        ("debate", run_debate),
    ]

    results = []

    for case in test_cases:
        query = case["query"]
        logger.info("Running: %s", case["id"])

        for mode_name, mode_fn in modes:
            logger.info("  Mode: %s...", mode_name)
            try:
                report, elapsed, corrections = await mode_fn(query)
                scores = await evaluate_output(query, report)

                results.append({
                    "case_id": case["id"],
                    "mode": mode_name,
                    "difficulty": case.get("difficulty", "unknown"),
                    "category": case.get("category", "unknown"),
                    "scores": scores,
                    "elapsed_sec": round(elapsed, 1),
                    "corrections": corrections,
                    "report_len": len(report),
                })
            except Exception as exc:
                logger.error("  FAILED: %s — %s", mode_name, exc)
                results.append({
                    "case_id": case["id"],
                    "mode": mode_name,
                    "scores": {"faithfulness": 0, "relevance": 0, "coherence": 0, "comment": str(exc)},
                    "elapsed_sec": 0,
                    "corrections": 0,
                    "report_len": 0,
                })

            await asyncio.sleep(1)  # rate limiting

    # --- Summary ---
    summary = _compute_summary(results, test_cases)

    # --- Write results ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = BENCHMARK_DIR / "results" / f"comparison_report_{timestamp}.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "summary": summary}, f, ensure_ascii=False, indent=2)

    # Also write latest for the dashboard
    latest_path = BENCHMARK_DIR / "results" / "comparison_report.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "summary": summary}, f, ensure_ascii=False, indent=2)

    logger.info("Results saved to: %s", results_path)
    _print_summary(summary)


def _compute_summary(results: list, test_cases: list) -> dict:
    """Aggregate scores by mode, difficulty, and category."""
    modes = ["baseline_single", "single_critic", "multi_round", "debate"]

    # ── Overall summary ──
    overall = {}
    for mode in modes:
        mode_results = [r for r in results if r["mode"] == mode]
        if not mode_results:
            continue
        avg = {
            "faithfulness": round(sum(r["scores"].get("faithfulness", 0) for r in mode_results) / len(mode_results), 2),
            "relevance": round(sum(r["scores"].get("relevance", 0) for r in mode_results) / len(mode_results), 2),
            "coherence": round(sum(r["scores"].get("coherence", 0) for r in mode_results) / len(mode_results), 2),
            "elapsed_sec": round(sum(r.get("elapsed_sec", 0) for r in mode_results) / len(mode_results), 1),
        }
        avg["overall"] = round((avg["faithfulness"] + avg["relevance"] + avg["coherence"]) / 3, 2)
        overall[mode] = avg

    # ── Per-difficulty breakdown ──
    difficulties = ["easy", "medium", "hard"]
    by_difficulty = {}
    for diff in difficulties:
        diff_results = [r for r in results if r.get("difficulty") == diff]
        mode_scores = {}
        for mode in modes:
            mr = [r for r in diff_results if r["mode"] == mode]
            if mr:
                mode_scores[mode] = round(
                    sum(r["scores"].get("faithfulness", 0) + r["scores"].get("relevance", 0) + r["scores"].get("coherence", 0)
                        for r in mr) / (len(mr) * 3), 2
                )
        by_difficulty[diff] = mode_scores

    # ── Per-category breakdown ──
    categories = sorted(set(r.get("category", "unknown") for r in results))
    by_category = {}
    for cat in categories:
        cat_results = [r for r in results if r.get("category") == cat]
        mode_scores = {}
        for mode in modes:
            mr = [r for r in cat_results if r["mode"] == mode]
            if mr:
                mode_scores[mode] = round(
                    sum(r["scores"].get("faithfulness", 0) + r["scores"].get("relevance", 0) + r["scores"].get("coherence", 0)
                        for r in mr) / (len(mr) * 3), 2
                )
        by_category[cat] = mode_scores

    # ── Key findings ──
    best_overall = max(overall.items(), key=lambda x: x[1]["overall"])
    fastest = min(overall.items(), key=lambda x: x[1]["elapsed_sec"])
    most_faithful = max(overall.items(), key=lambda x: x[1]["faithfulness"])

    findings = [
        f"🥇 {best_overall[0]} 综合得分最高 ({best_overall[1]['overall']:.2f})",
        f"⚡ {fastest[0]} 速度最快 ({fastest[1]['elapsed_sec']:.1f}s)",
        f"📚 {most_faithful[0]} 忠实度最优 ({most_faithful[1]['faithfulness']:.2f})",
    ]
    # Multi-round vs single-critic comparison
    if "multi_round" in overall and "single_critic" in overall:
        mr = overall["multi_round"]["overall"]
        sc = overall["single_critic"]["overall"]
        diff = mr - sc
        if diff < 0:
            findings.append(f"⚠️ 多轮反思比单审查低 {abs(diff):.2f} 分 — 压缩环节存在信息损失")
        else:
            findings.append(f"✅ 多轮反思优于单审查 +{diff:.2f} 分")
    # Debate vs single-critic
    if "debate" in overall and "single_critic" in overall:
        db = overall["debate"]["overall"]
        sc = overall["single_critic"]["overall"]
        diff = db - sc
        if diff > 0:
            findings.append(f"🏆 辩论模式优于单审查 +{diff:.2f} 分 — 并行多元审查 > 串行反复修改")

    return {
        "overall": overall,
        "by_difficulty": by_difficulty,
        "by_category": by_category,
        "key_findings": findings,
    }


def _print_summary(summary: dict):
    overall = summary["overall"]

    print("\n" + "=" * 80)
    print("  BENCHMARK RESULTS — Multi-Agent Reflective Solver")
    print("=" * 80)

    # ── Overall table ──
    print("\n📊 综合评分 (0-10):")
    print(f"{'Mode':<22} {'忠实度':<8} {'相关性':<8} {'连贯性':<8} {'综合':<8} {'耗时(s)':<10}")
    print("-" * 80)
    for mode, scores in overall.items():
        name = {
            "baseline_single": "Baseline (单轮)",
            "single_critic": "单审查模式",
            "multi_round": "多轮反思 (3轮)",
            "debate": "辩论模式 (3审查)",
        }.get(mode, mode)
        print(
            f"{name:<22} "
            f"{scores['faithfulness']:<8.2f} "
            f"{scores['relevance']:<8.2f} "
            f"{scores['coherence']:<8.2f} "
            f"{scores['overall']:<8.2f} "
            f"{scores['elapsed_sec']:<10.1f}"
        )

    # ── Per-difficulty ──
    if summary.get("by_difficulty"):
        print("\n📈 按难度分层的综合得分:")
        print(f"{'难度':<12}", end="")
        modes_order = ["baseline_single", "single_critic", "multi_round", "debate"]
        mode_names = ["Baseline", "单审查", "多轮反思", "辩论"]
        for mn in mode_names:
            print(f"{mn:<12}", end="")
        print()
        print("-" * 60)
        for diff in ["easy", "medium", "hard"]:
            scores = summary["by_difficulty"].get(diff, {})
            print(f"{diff:<12}", end="")
            for mode in modes_order:
                s = scores.get(mode, "-")
                if isinstance(s, (int, float)):
                    print(f"{s:<12.2f}", end="")
                else:
                    print(f"{'-':<12}", end="")
            print()

    # ── Key findings ──
    print("\n🔍 关键发现:")
    for finding in summary.get("key_findings", []):
        print(f"  {finding}")

    print("\n" + "=" * 80)

    # ── Top recommendation ──
    if overall:
        best = max(overall.items(), key=lambda x: x[1]["overall"])
        print(f"\n💡 推荐生产模式: {best[0]} (综合 {best[1]['overall']:.2f})")
        print(f"   > 打开 benchmark/dashboard.html 查看交互式可视化对比。")
        print(f"   > 压测命令: locust -f locustfile.py --host=http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(main())
