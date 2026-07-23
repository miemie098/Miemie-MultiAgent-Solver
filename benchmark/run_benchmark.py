#!/usr/bin/env python
"""
Automated benchmark — compares 4 solver modes across 10+ test cases.

Bias-elimination measures:
  1. Mode order randomized per test case (eliminates position bias)
  2. Dual-judge cross-validation (eliminates single-model judge bias)
  3. Repeated runs with mean ± stddev (quantifies variance)

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
  python benchmark/run_benchmark.py              # default: 1 repeat, 1 judge
  python benchmark/run_benchmark.py --repeat 3   # 3 repeats for stddev
  python benchmark/run_benchmark.py --dual       # dual-judge cross-validation
  python benchmark/run_benchmark.py --repeat 3 --dual  # both
"""
import asyncio
import json
import logging
import os
import random
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

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger("benchmark")
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Judge
# ---------------------------------------------------------------------------
def _get_primary_judge():
    """Primary judge: DeepSeek-Chat at temperature=0 (deterministic)."""
    return LLMFactory.get_llm(temperature=0.0)


def _get_secondary_judge():
    """Secondary judge for cross-validation.

    Configure via SECOND_JUDGE_* env vars. Defaults to the same model
    but with a different prompt style — still better than a single judge.
    To use a truly independent judge (e.g. GPT-4), set:
      SECOND_JUDGE_API_KEY=sk-...
      SECOND_JUDGE_BASE_URL=https://api.openai.com/v1
      SECOND_JUDGE_MODEL=gpt-4
    """
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("SECOND_JUDGE_API_KEY")
    if not api_key:
        return None  # dual-judge not configured

    return ChatOpenAI(
        model=os.getenv("SECOND_JUDGE_MODEL", "deepseek-chat"),
        temperature=0.0,
        openai_api_key=api_key,
        openai_api_base=os.getenv(
            "SECOND_JUDGE_BASE_URL", "https://api.deepseek.com/v1"
        ),
        max_retries=2,
        request_timeout=60,
    )


JUDGE_PROMPT = """作为 AI 架构评估专家，请对以下回答评分（0-10 整数）。评分时请忽略答案的长度和风格，只关注技术内容本身。

【任务】：{task}
【待评回答】：{response}

评分维度：
1. faithfulness (忠实度)：回答是否基于合理的技术事实，无明显编造或幻觉？
2. relevance (相关性)：是否直接解决了问题，而非泛泛而谈？
3. coherence (连贯性)：结构是否清晰，逻辑是否自洽，是否存在前后矛盾？

请严格返回 JSON（不要包含 Markdown 代码块标记）：
{{"faithfulness": 0, "relevance": 0, "coherence": 0, "comment": "一句话评语"}}"""

# Secondary judge uses a slightly different prompt to avoid rote agreement
JUDGE_PROMPT_V2 = """你是一名独立的 AI 系统评审专家。请严格评估以下技术回答的质量。

【任务】：{task}
【待评回答】：{response}

请从以下三个维度独立评分（0-10 整数，禁止给所有人打中间分 5/6/7，必须有区分度）：

1. 技术准确性：事实引用是否准确？是否存在幻觉或概念混淆？
2. 方案完备性：是否给出具体可操作的方案，而非空洞概述？
3. 表达清晰度：逻辑链条是否完整，结论是否有充分支撑？

严格只输出 JSON：
{{"accuracy": 0, "completeness": 0, "clarity": 0, "comment": "一句话评语"}}"""


async def evaluate_output(task: str, response: str, judge, prompt_template: str,
                           score_map: dict) -> dict:
    """Run one judge on one answer. score_map renames keys to standard names."""
    prompt = prompt_template.format(task=task, response=response)
    try:
        res = await judge.ainvoke([HumanMessage(content=prompt)])
        match = re.search(r"\{.*\}", res.content, re.DOTALL)
        if match:
            raw = json.loads(match.group())
            # Map judge-specific keys to standard names
            return {
                "faithfulness": raw.get(score_map.get("faithfulness", "faithfulness"), 0),
                "relevance": raw.get(score_map.get("relevance", "relevance"), 0),
                "coherence": raw.get(score_map.get("coherence", "coherence"), 0),
                "comment": raw.get("comment", ""),
            }
    except Exception as exc:
        logger.warning("Judge failed: %s", exc)
    return {"faithfulness": 0, "relevance": 0, "coherence": 0, "comment": "评分解析失败"}


async def dual_evaluate(task: str, response: str, judge2) -> dict:
    """Run both judges and return averaged scores + agreement metrics."""
    judge1 = _get_primary_judge()

    s1_map = {"faithfulness": "faithfulness", "relevance": "relevance", "coherence": "coherence"}
    s2_map = {"faithfulness": "accuracy", "relevance": "completeness", "coherence": "clarity"}

    s1, s2 = await asyncio.gather(
        evaluate_output(task, response, judge1, JUDGE_PROMPT, s1_map),
        evaluate_output(task, response, judge2, JUDGE_PROMPT_V2, s2_map),
    )

    # Average scores
    avg = {
        "faithfulness": round((s1["faithfulness"] + s2["faithfulness"]) / 2, 1),
        "relevance": round((s1["relevance"] + s2["relevance"]) / 2, 1),
        "coherence": round((s1["coherence"] + s2["coherence"]) / 2, 1),
    }

    # Inter-rater agreement (Pearson-like simple correlation on 3D vector)
    import statistics
    diffs = [
        abs(s1["faithfulness"] - s2["faithfulness"]),
        abs(s1["relevance"] - s2["relevance"]),
        abs(s1["coherence"] - s2["coherence"]),
    ]
    agreement = round(1.0 - statistics.mean(diffs) / 10.0, 3)  # normalized to [0,1]

    return {
        **avg,
        "comment": f"J1: {s1.get('comment', '')} | J2: {s2.get('comment', '')}",
        "agreement": agreement,
        "judge1": s1,
        "judge2": s2,
    }


# ---------------------------------------------------------------------------
# Mode runners
# ---------------------------------------------------------------------------
async def run_baseline_single(query: str) -> tuple:
    from app.agents.analyzer_agent import AnalyzerAgent
    from app.agents.summary_agent import SummaryAgent

    state = {"query": query, "paper_context": "", "compressed_context": "", "history_logs": []}

    start = time.time()
    analyzer = AnalyzerAgent()
    result = await analyzer.run(state)
    summary = SummaryAgent()
    final = await summary.run({**state, **result})
    elapsed = time.time() - start
    return final.get("final_report", ""), elapsed, 1


async def run_single_critic(query: str) -> tuple:
    from app.graph.workflow import create_workflow
    import os as _os
    _os.environ["DEBATE_MODE"] = "single"
    workflow = create_workflow()
    start = time.time()
    final = await workflow.ainvoke(_make_state(query, max_corrections=1))
    elapsed = time.time() - start
    return final.get("final_report", ""), elapsed, final.get("correction_count", 1)


async def run_multi_round(query: str) -> tuple:
    from app.graph.workflow import create_workflow
    import os as _os
    _os.environ["DEBATE_MODE"] = "single"
    workflow = create_workflow()
    start = time.time()
    final = await workflow.ainvoke(_make_state(query, max_corrections=3))
    elapsed = time.time() - start
    return final.get("final_report", ""), elapsed, final.get("correction_count", 1)


async def run_debate(query: str) -> tuple:
    from app.graph.workflow import create_workflow
    import os as _os
    _os.environ["DEBATE_MODE"] = "debate"
    workflow = create_workflow()
    start = time.time()
    final = await workflow.ainvoke(_make_state(query, max_corrections=3))
    elapsed = time.time() - start
    return final.get("final_report", ""), elapsed, final.get("correction_count", 1)


def _make_state(query: str, max_corrections: int) -> dict:
    return {
        "query": query, "paper_context": "", "max_corrections": max_corrections,
        "correction_count": 0, "history_logs": [], "search_output": {},
        "analyzer_output": {}, "critic_output": {}, "compactor_output": {},
        "summary_output": {}, "compressed_context": "", "final_report": "",
    }


# ---------------------------------------------------------------------------
# Aggregation with variance
# ---------------------------------------------------------------------------
def _mean_std(values: list) -> tuple:
    """Return (mean, stddev) for a list of floats. Returns (0,0) if empty."""
    if not values:
        return 0.0, 0.0
    import statistics
    mu = statistics.mean(values)
    sigma = statistics.stdev(values) if len(values) >= 2 else 0.0
    return round(mu, 2), round(sigma, 2)


def _compute_summary(results: list, repeat: int) -> dict:
    """Aggregate scores by mode, with stddev from repeated runs."""
    modes = ["baseline_single", "single_critic", "multi_round", "debate"]
    overall = {}
    for mode in modes:
        mode_results = [r for r in results if r["mode"] == mode]
        if not mode_results:
            continue

        faith_vals = [r["scores"].get("faithfulness", 0) for r in mode_results]
        relev_vals = [r["scores"].get("relevance", 0) for r in mode_results]
        coher_vals = [r["scores"].get("coherence", 0) for r in mode_results]
        overall_vals = [
            (r["scores"].get("faithfulness", 0) + r["scores"].get("relevance", 0) + r["scores"].get("coherence", 0)) / 3
            for r in mode_results
        ]
        elapsed_vals = [r.get("elapsed_sec", 0) for r in mode_results]

        f_m, f_s = _mean_std(faith_vals)
        r_m, r_s = _mean_std(relev_vals)
        c_m, c_s = _mean_std(coher_vals)
        o_m, o_s = _mean_std(overall_vals)
        e_m, e_s = _mean_std(elapsed_vals)

        overall[mode] = {
            "faithfulness": f_m, "faithfulness_std": f_s,
            "relevance": r_m, "relevance_std": r_s,
            "coherence": c_m, "coherence_std": c_s,
            "overall": o_m, "overall_std": o_s,
            "elapsed_sec": e_m, "elapsed_std": e_s,
            "samples": len(mode_results),
        }

    # ── Inter-rater agreement (if dual-judge) ──
    agreements = [r["scores"].get("agreement") for r in results
                  if r["scores"].get("agreement") is not None]
    avg_agreement = round(sum(agreements) / len(agreements), 3) if agreements else None

    # ── Key findings ──
    findings = []
    if overall:
        best = max(overall.items(), key=lambda x: x[1]["overall"])
        findings.append(
            f"🥇 {best[0]} 综合 {best[1]['overall']} ± {best[1]['overall_std']} "
            f"(n={best[1]['samples']})"
        )
        if "multi_round" in overall and "single_critic" in overall:
            mr = overall["multi_round"]["overall"]
            sc = overall["single_critic"]["overall"]
            gap = abs(mr - sc)
            findings.append(
                f"⚠️ 多轮反思 vs 单审查差距: {gap:.2f} 分"
                + (f" (多轮更低，印证 Compactor 信息损失)" if mr < sc else "")
            )
        if "debate" in overall and "single_critic" in overall:
            db = overall["debate"]["overall"]
            sc = overall["single_critic"]["overall"]
            gap = db - sc
            findings.append(
                f"🏆 辩论 vs 单审查: {'+' if gap > 0 else ''}{gap:.2f} 分"
            )
    if avg_agreement is not None:
        findings.append(f"📊 双 Judge 一致率: {avg_agreement:.3f} (1.0=完全一致)")

    return {
        "overall": overall,
        "repeat": repeat,
        "inter_rater_agreement": avg_agreement,
        "key_findings": findings,
    }


def _print_summary(summary: dict):
    overall = summary["overall"]

    print("\n" + "=" * 90)
    print("  BENCHMARK RESULTS — Multi-Agent Reflective Solver")
    if summary.get("repeat", 1) > 1:
        print(f"  (repeat={summary['repeat']}, scores shown as mean ± stddev)")
    if summary.get("inter_rater_agreement"):
        print(f"  (dual-judge mode, inter-rater agreement = {summary['inter_rater_agreement']:.3f})")
    print("=" * 90)

    print(f"\n{'Mode':<22} {'忠实度':<14} {'相关性':<14} {'连贯性':<14} {'综合':<14} {'耗时(s)':<14}")
    print("-" * 90)
    for mode, s in overall.items():
        name = {
            "baseline_single": "Baseline (单轮)",
            "single_critic": "单审查",
            "multi_round": "多轮反思",
            "debate": "辩论 (3审查)",
        }.get(mode, mode)
        if s.get("overall_std", 0) > 0:
            print(
                f"{name:<22} "
                f"{s['faithfulness']}±{s['faithfulness_std']:<7} "
                f"{s['relevance']}±{s['relevance_std']:<7} "
                f"{s['coherence']}±{s['coherence_std']:<7} "
                f"{s['overall']}±{s['overall_std']:<7} "
                f"{s['elapsed_sec']}±{s['elapsed_std']:<7}"
            )
        else:
            print(
                f"{name:<22} "
                f"{s['faithfulness']:<14.2f} {s['relevance']:<14.2f} "
                f"{s['coherence']:<14.2f} {s['overall']:<14.2f} "
                f"{s['elapsed_sec']:<14.1f}"
            )

    print("\n🔍 关键发现:")
    for f in summary.get("key_findings", []):
        print(f"  {f}")
    print("=" * 90)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=1, help="Repeat each mode×case N times for stddev")
    ap.add_argument("--dual", action="store_true", help="Enable dual-judge cross-validation")
    ap.add_argument("--seed", type=int, default=None, help="Random seed for reproducible shuffles")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    with open(BENCHMARK_DIR / "test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    # ── Judges ──
    judge2 = _get_secondary_judge() if args.dual else None
    if args.dual and judge2 is None:
        logger.warning(
            "--dual specified but SECOND_JUDGE_API_KEY not set. "
            "Falling back to single-judge mode."
        )

    logger.info(
        "Benchmark: %d cases × 4 modes × %d repeats = %d runs, dual_judge=%s",
        len(test_cases), args.repeat, len(test_cases) * 4 * args.repeat,
        args.dual and judge2 is not None,
    )

    mode_defs = [
        ("baseline_single", run_baseline_single),
        ("single_critic", run_single_critic),
        ("multi_round", run_multi_round),
        ("debate", run_debate),
    ]

    results = []
    order_log = []  # audit trail for position bias analysis

    for case in test_cases:
        query = case["query"]
        case_id = case["id"]
        logger.info("Case: %s", case_id)

        for rep in range(args.repeat):
            # ── Shuffle mode order per case×repeat (eliminates position bias) ──
            shuffled = list(mode_defs)
            random.shuffle(shuffled)
            order_log.append({
                "case_id": case_id,
                "repeat": rep,
                "order": [m[0] for m in shuffled],
            })

            for mode_name, mode_fn in shuffled:
                if args.repeat > 1:
                    logger.info("  %s [rep %d/%d] ...", mode_name, rep + 1, args.repeat)
                else:
                    logger.info("  %s ...", mode_name)

                try:
                    report, elapsed, corrections = await mode_fn(query)

                    if args.dual and judge2 is not None:
                        scores = await dual_evaluate(query, report, judge2)
                    else:
                        s1_map = {"faithfulness": "faithfulness", "relevance": "relevance", "coherence": "coherence"}
                        scores = await evaluate_output(query, report, _get_primary_judge(), JUDGE_PROMPT, s1_map)

                    results.append({
                        "case_id": case_id,
                        "mode": mode_name,
                        "repeat": rep,
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
                        "case_id": case_id,
                        "mode": mode_name,
                        "repeat": rep,
                        "difficulty": case.get("difficulty", "unknown"),
                        "category": case.get("category", "unknown"),
                        "scores": {"faithfulness": 0, "relevance": 0, "coherence": 0, "comment": str(exc)},
                        "elapsed_sec": 0,
                        "corrections": 0,
                        "report_len": 0,
                    })

                await asyncio.sleep(1)  # rate limiting

    # ── Summary ──
    summary = _compute_summary(results, args.repeat)

    # ── Write results ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_r{args.repeat}" + ("_dual" if args.dual else "")
    results_path = BENCHMARK_DIR / "results" / f"comparison_report_{timestamp}{suffix}.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({
            "config": {"repeat": args.repeat, "dual_judge": args.dual, "seed": args.seed},
            "results": results,
            "summary": summary,
            "order_log": order_log,
        }, f, ensure_ascii=False, indent=2)

    latest_path = BENCHMARK_DIR / "results" / "comparison_report.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump({
            "config": {"repeat": args.repeat, "dual_judge": args.dual, "seed": args.seed},
            "results": results,
            "summary": summary,
            "order_log": order_log,
        }, f, ensure_ascii=False, indent=2)

    logger.info("Results saved to: %s", results_path)
    _print_summary(summary)


if __name__ == "__main__":
    asyncio.run(main())
