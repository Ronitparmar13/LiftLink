"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongodb_uri: str = ""
    firebase_service_account_json: str = "./firebase-service-account.json"
    allowed_email_domain: str = "paruluniversity.ac.in"
    geo_match_radius_meters: int = 500
    fuel_split_rate_per_km: float = 3.5
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Parul University campus bounding box (PRD Section 3.2)
    campus_min_lng: float = 73.18
    campus_min_lat: float = 22.28
    campus_max_lng: float = 73.25
    campus_max_lat: float = 22.35

    def is_within_campus_bounds(self, lng: float, lat: float) -> bool:
        return (
            self.campus_min_lng <= lng <= self.campus_max_lng
            and self.campus_min_lat <= lat <= self.campus_max_lat
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def firebase_credentials_path(self) -> Path:
        return Path(self.firebase_service_account_json)


@lru_cache
def get_settings() -> Settings:
    return Settings()
