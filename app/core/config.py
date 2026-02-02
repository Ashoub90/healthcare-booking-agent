from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Healthcare Booking Agent"
    debug: bool = False
    database_url: str = "sqlite:///./data.db"

    class Config:
        env_file = ".env"


settings = Settings()
