from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_bot_token: str = ""
    database_url: str = "sqlite+aiosqlite:///data/axenda.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    log_level: str = "DEBUG"
    default_city: str = "Gijón"


settings = Settings()
