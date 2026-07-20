"""
Long-context stress test for DeepSeek API.
Tests whether the server handles large prompts without connection drops.
Usage: python test_lc.py
"""
import asyncio
import os
from openai import AsyncOpenAI


async def test_long_prompt():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not set.")
        return

    print("🚀 Sending long-context prompt to DeepSeek...")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1")
    )

    long_text = "This is a test sentence. " * 500

    try:
        res = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": f"Summarize:\n{long_text}"}],
            timeout=60.0
        )
        print(f"✅ Success! Server handled {len(long_text)} chars without dropping connection.")
    except Exception as e:
        print(f"❌ Long-context request failed: {type(e).__name__}: {e}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(test_long_prompt())
