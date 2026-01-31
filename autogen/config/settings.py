from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm: str = "openrouter/google/gemini-3-flash-preview"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
