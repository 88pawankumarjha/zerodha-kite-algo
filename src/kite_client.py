from __future__ import annotations

from kiteconnect import KiteConnect

from .config import TOKEN_FILE, load_settings, require_api_credentials


def build_kite_client() -> KiteConnect:
    settings = load_settings()
    require_api_credentials(settings)

    if not TOKEN_FILE.exists():
        raise RuntimeError("Missing .kite_access_token. Run: python -m src.auth_login")

    kite = KiteConnect(api_key=settings.api_key)
    kite.set_access_token(TOKEN_FILE.read_text(encoding="utf-8").strip())
    return kite
