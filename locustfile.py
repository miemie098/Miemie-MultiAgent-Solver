"""
Locust load-testing script for Miemie-MultiAgent-Solver.

Usage:
    locust -f locustfile.py --host=http://localhost:8000
    Then open http://localhost:8089, set users/spawn rate, and start.

Tests the streaming endpoint (/api/solve/stream) which exercises the full
multi-agent workflow: Search → Analyze → Critic → Compactor → Summary.
"""
import random
from locust import HttpUser, task, between


# Representative AI infrastructure queries from the benchmark suite
QUERIES = [
    "分析 PagedAttention 机制的显存优化原理及其对高并发推理吞吐的影响",
    "FlashAttention 如何通过 IO-aware 算法减少 HBM 访问？",
    "投机解码（Speculative Decoding）的加速原理是什么？",
    "比较 GPTQ、AWQ 和 QLoRA 三种量化方法的适用场景和性能差异",
    "Mixture of Experts (MoE) 架构在高并发推理时面临的负载均衡挑战",
    "分析 StreamingLLM 和 H2O 两种 KV cache 淘汰策略的异同",
    "RoPE 位置编码相比绝对位置编码有哪些优势？",
    "大模型分布式推理中，Tensor Parallelism 和 Pipeline Parallelism 如何组合？",
]


class SolverUser(HttpUser):
    """Simulates users solving AI infrastructure analysis problems."""

    wait_time = between(5, 15)

    @task(3)
    def solve_stream(self):
        """Stream endpoint — exercises the full multi-agent workflow."""
        query = random.choice(QUERIES)
        with self.client.post(
            "/api/solve/stream",
            json={"query": query, "max_corrections": 2},
            stream=True,
            catch_response=True,
            timeout=120,
        ) as response:
            if response.status_code == 200:
                # Consume SSE stream to completion
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith("data:"):
                        pass  # event consumed
                response.success()
            else:
                response.failure(f"Stream failed: {response.status_code}")

    @task(1)
    def health_check(self):
        """Lightweight health check — baseline latency metric."""
        self.client.get("/api/health")

    @task(2)
    def solve_sync(self):
        """Non-streaming endpoint — full workflow in one response."""
        query = random.choice(QUERIES)
        with self.client.post(
            "/api/solve",
            json={"query": query, "max_corrections": 3},
            catch_response=True,
            timeout=120,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Solve failed: {response.status_code}")
