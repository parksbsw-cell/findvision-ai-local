from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FINDVISION_", env_file=".env")

    data_dir: Path = Path("data")
    image_model: str = "stabilityai/stable-diffusion-xl-base-1.0"
    verifier_model: str = "qwen2.5vl:3b"
    ollama_url: str = "http://127.0.0.1:11434"
    max_attempts: int = 3
    max_message_chars: int = 1800
    rate_limit_per_hour: int = 20
    mock_generation: bool = False
    admin_token: str = ""


settings = Settings()

