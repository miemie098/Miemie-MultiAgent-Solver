import os
import requests
from pathlib import Path

# 目标根目录（与您之前的相同）
DATA_DIR = Path(r"D:\projects\Miemie-MultiAgent-Solver\data")

# 已存在的文件列表（基于您日志中的成功文件，用于跳过）
EXISTING_FILES = {
    # PDFs
    "Vaswani-2017-Attention-Is-All-You-Need.pdf",
    "Dao-2022-FlashAttention.pdf",
    "Dao-2023-FlashAttention-2.pdf",
    "Dao-2024-FlashAttention-3.pdf",
    "Leviathan-2022-SpeculativeDecoding.pdf",
    "Frantar-2022-GPTQ.pdf",
    "Lin-2023-AWQ.pdf",
    "Dettmers-2023-QLoRA.pdf",
    "Kwon-2023-vLLM-PagedAttention.pdf",
    "Su-2021-RoPE.pdf",
    "Press-2021-ALiBi.pdf",
    "Peng-2023-YaRN.pdf",
    "Xiao-2023-StreamingLLM.pdf",
    "Fedus-2021-Switch-Transformer.pdf",
    "Lepikhin-2020-GShard.pdf",
    "Zoph-2022-ST-MoE.pdf",
    "Jiang-2024-Mixtral-Of-Experts.pdf",
    # Markdowns
    "vLLM-Documentation.md",
    "Meta-LLaMA-3-ModelCard.md",
    "DeepSpeed-README.md",
    "Megatron-LM-README.md",
    "HF-KVCache-Guide.md",
    "PyTorch-SDPA-FlashAttention2.md",
}

# 新的下载列表（替换失效 + 额外补充）
NEW_DOWNLOADS = [
    # ---- 替换失效的 DeepSeek-V3.pdf ----
    # 使用 DeepSeek-V2 论文（大小约2MB，来自arxiv）
    ("https://arxiv.org/pdf/2405.04434", "DeepSeek-V2.pdf"),

    # ---- 替换失效的 NVIDIA-TensorRT-LLM.md ----
    # 使用 TensorRT-LLM 官方文档（GitHub README，转为 .md 保存）
    ("https://raw.githubusercontent.com/NVIDIA/TensorRT-LLM/main/README.md", "NVIDIA-TensorRT-LLM.md"),

    # ---- 额外补充论文（推理加速方向）----
    # 1. SpecInfer: 投机解码改进（约500KB）
    ("https://arxiv.org/pdf/2301.11542", "Miao-2023-SpecInfer.pdf"),
    # 2. Medusa: 多头投机解码（约1.2MB）
    ("https://arxiv.org/pdf/2401.04574", "Cai-2024-Medusa.pdf"),
    # 3. Skeleton-of-Thought: 并行解码（约800KB）
    ("https://arxiv.org/pdf/2307.15337", "Ning-2023-Skeleton-of-Thought.pdf"),
    # 4. Blockwise Parallel Decoding（约600KB）
    ("https://arxiv.org/pdf/2311.05722", "Stern-2023-BlockwiseParallel.pdf"),
    # 5. LLM.int8(): 8-bit 量化（约400KB）
    ("https://arxiv.org/pdf/2208.07339", "Dettmers-2022-LLMint8.pdf"),
    # 6. SmoothQuant: 平滑量化（约900KB）
    ("https://arxiv.org/pdf/2211.10438", "Xiao-2022-SmoothQuant.pdf"),
    # 7. SpAtten: 稀疏注意力（约1.5MB）
    ("https://arxiv.org/pdf/2204.02353", "Wang-2022-SpAtten.pdf"),
    # 8. H2O: 高效KV缓存淘汰（约700KB）
    ("https://arxiv.org/pdf/2306.14048", "Zhang-2023-H2O.pdf"),
    # 9. Scissorhands: KV缓存压缩（约600KB）
    ("https://arxiv.org/pdf/2305.17118", "Liu-2023-Scissorhands.pdf"),
    # 10. FastGen: 注意力掩码优化（约500KB）
    ("https://arxiv.org/pdf/2210.06423", "Dao-2022-FastGen.pdf"),
]

def download_file(url, filename):
    """下载单个文件，跳过已存在的"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        print(f"⏭️ 已存在，跳过: {filename}")
        return False
    try:
        print(f"⬇️ 下载: {filename} ...", end=" ")
        resp = requests.get(url, timeout=30, allow_redirects=True)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(resp.content)
        size_mb = len(resp.content) / (1024 * 1024)
        print(f"✓ ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

def main():
    print("开始增量下载新论文...")
    total_added = 0
    for url, name in NEW_DOWNLOADS:
        if download_file(url, name):
            total_added += 1
    print(f"\n✅ 完成！共新增 {total_added} 个文件。")
    print("现有总大小约 39.9 MB + 新增 ≈ 60~70 MB（视网络情况略有差异）")

if __name__ == "__main__":
    main()