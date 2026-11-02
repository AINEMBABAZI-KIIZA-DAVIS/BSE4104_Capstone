from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Settings:
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    dashboard_port: int = int(os.getenv("DASHBOARD_PORT", "8001"))
    debug: bool = os.getenv("DEBUG", "0").lower() in {"1", "true", "yes", "on"}
    allowed_origins: Tuple[str, ...] = tuple(
        item.strip() for item in os.getenv("ALLOWED_ORIGINS", "*").split(",") if item.strip()
    )

    @property
    def cors_origins(self) -> list[str]:
        return ["*"] if self.allowed_origins == ("*",) else list(self.allowed_origins)


settings = Settings()
