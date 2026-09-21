"""Configuration settings for Part 2 AI Attacker Application."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AttackerConfig:
    """Attacker application configuration."""

    HOST: str = os.getenv("ATTACKER_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("ATTACKER_PORT", "8001"))
    GATEWAY_BASE_URL: str = os.getenv(
        "ATTACKER_GATEWAY_BASE_URL", "http://127.0.0.1:8000/api/attacker"
    ).rstrip("/")
    GATEWAY_TOKEN: str | None = os.getenv("ATTACK_GATEWAY_TOKEN", None)
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY", os.getenv("ATTACKER_LLM_API_KEY", None))
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY", None)
    ATTACKER_LLM_PROVIDER: str = os.getenv("ATTACKER_LLM_PROVIDER", "openai")
    ATTACKER_LLM_MODEL: str = os.getenv("ATTACKER_LLM_MODEL", "gpt-4o-mini")
    REQUEST_TIMEOUT: float = float(os.getenv("ATTACKER_TIMEOUT", "10.0"))


config = AttackerConfig()

