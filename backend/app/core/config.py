from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    secret_key: str
    frontend_url: str = "http://localhost:3000"

    database_url: str
    test_database_url: str | None = None

    email_verification_otp_expire_minutes: int = 10
    email_verification_otp_max_attempts: int = 5

    access_token_expire_days: int = 7
    access_token_remember_me_expire_days: int = 30

    cookie_secure: bool = False
    cookie_samesite: str = "lax"

    password_reset_otp_expire_minutes: int = 10
    password_reset_otp_max_attempts: int = 5

    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    smtp_use_tls: bool = True

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
