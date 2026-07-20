"""
LLM Factory — unified model access gateway with retry, timeout, and env loading.

Uses the singleton factory pattern. All agents call LLMFactory.get_llm()
to obtain a configured ChatOpenAI instance pointed at DeepSeek's API.
"""
import os
import logging

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Resolve .env path relative to project root (defensive against cwd changes)
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))   # app/agents/
_APP_DIR = os.path.dirname(_CURRENT_DIR)                     # app/
_PROJECT_ROOT = os.path.dirname(_APP_DIR)                    # repo root
_ENV_PATH = os.path.join(_PROJECT_ROOT, ".env")

if os.path.exists(_ENV_PATH):
    load_dotenv(_ENV_PATH, override=True)
else:
    load_dotenv()  # fallback: try cwd

logger = logging.getLogger("miemie.llm")


class LLMFactory:
    """Singleton factory for LangChain ChatOpenAI instances.

    Reads DEEPSEEK_API_KEY and OPENAI_API_BASE from environment.
    All instances share the same underlying httpx connection pool.
    """

    @classmethod
    def get_llm(cls, temperature: float = 0.0) -> ChatOpenAI:
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE") or "https://api.deepseek.com/v1"

        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not found in environment. "
                f"Create a .env file at {_ENV_PATH} with your key. "
                "See .env.example for the format."
            )

        logger.debug("Creating LLM client: model=deepseek-chat, temperature=%.2f", temperature)

        return ChatOpenAI(
            model="deepseek-chat",
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base=base_url,
            max_retries=3,            # LangChain built-in retry with backoff
            request_timeout=60,       # 60s timeout per request
        )
