from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Krevera Analytics API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "krevera"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    TEMPORAL_HOST: str = "temporal"
    TEMPORAL_PORT: int = 7233

    @property
    def TEMPORAL_URL(self) -> str:
        return f"{self.TEMPORAL_HOST}:{self.TEMPORAL_PORT}"

    S3_ENDPOINT_URL: str = "http://localstack:4566"
    S3_BUCKET_NAME: str = "krevera-datasets"
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_REGION: str = "us-east-1"

    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()