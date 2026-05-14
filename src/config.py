from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - helpful before dependencies are installed
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = PROJECT_ROOT / ".kite_access_token"


if load_dotenv:
    load_dotenv(PROJECT_ROOT / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_secret: str
    redirect_url: str
    dry_run: bool
    live_trading_enabled: bool
    live_order_confirmation: str
    default_exchange: str
    default_product: str
    default_variety: str
    default_validity: str
    default_tag: str

    @property
    def can_place_live_orders(self) -> bool:
        return (
            not self.dry_run
            and self.live_trading_enabled
            and self.live_order_confirmation == "I_UNDERSTAND"
        )


def load_settings() -> Settings:
    return Settings(
        api_key=os.getenv("KITE_API_KEY", "").strip(),
        api_secret=os.getenv("KITE_API_SECRET", "").strip(),
        redirect_url=os.getenv("KITE_REDIRECT_URL", "").strip(),
        dry_run=_env_bool("DRY_RUN", True),
        live_trading_enabled=_env_bool("LIVE_TRADING_ENABLED", False),
        live_order_confirmation=os.getenv("CONFIRM_LIVE_ORDER", "").strip(),
        default_exchange=os.getenv("DEFAULT_EXCHANGE", "NFO").strip(),
        default_product=os.getenv("DEFAULT_PRODUCT", "MIS").strip(),
        default_variety=os.getenv("DEFAULT_VARIETY", "regular").strip(),
        default_validity=os.getenv("DEFAULT_VALIDITY", "DAY").strip(),
        default_tag=os.getenv("DEFAULT_TAG", "algo-dryrun").strip(),
    )


def require_api_credentials(settings: Settings) -> None:
    missing = []
    if not settings.api_key:
        missing.append("KITE_API_KEY")
    if not settings.api_secret:
        missing.append("KITE_API_SECRET")
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(f"Missing required environment value(s): {names}")
