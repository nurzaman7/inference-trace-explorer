"""Configuration model loaded from environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "inference-trace-explorer"
    env: str = "dev"
    trace_sample_rate: float = 1.0
    sqlite_path: str = "./data/trace_store.db"
    jsonl_trace_path: str = "./data/traces/traces.jsonl"
    activation_dir: str = "./data/activations"
    analytics_rollup_path: str = "./data/analytics/rollups.jsonl"
    rollup_interval_seconds: int = 60

    enable_redis: bool = False
    redis_url: str = "redis://redis:6379/0"

    # Provider integration defaults
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_api_key: str = ""
    anthropic_base_url: str = "https://api.anthropic.com"

    # Dashboard integration
    api_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
