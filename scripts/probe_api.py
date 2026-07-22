"""
Network connectivity probe for DeepSeek API.
Run this to verify your API key and network are correctly configured.
Usage: python test.py
"""
import asyncio
import os
from openai import AsyncOpenAI


async def check_network():
    print("🔍 [Probe] Testing direct connectivity to DeepSeek API...")

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not set in environment or .env file.")
        print("   Copy .env.example to .env and add your key.")
        return

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1"),
        max_retries=0
    )

    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "ping"}],
            timeout=15.0
        )
        print(f"✅ Connectivity OK! Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_network())
