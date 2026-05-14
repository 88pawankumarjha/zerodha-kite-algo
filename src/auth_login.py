from __future__ import annotations

import os
from getpass import getpass

from kiteconnect import KiteConnect

from .config import TOKEN_FILE, load_settings, require_api_credentials


def main() -> None:
    settings = load_settings()
    require_api_credentials(settings)

    kite = KiteConnect(api_key=settings.api_key)
    print("Open this URL in the intended browser profile:")
    print(kite.login_url())

    request_token = getpass("Paste request_token: ").strip()
    if not request_token:
        raise RuntimeError("request_token is required")

    session = kite.generate_session(request_token, api_secret=settings.api_secret)
    access_token = session["access_token"]

    TOKEN_FILE.write_text(access_token + "\n", encoding="utf-8")
    os.chmod(TOKEN_FILE, 0o600)
    print(f"Access token saved to {TOKEN_FILE.name}")


if __name__ == "__main__":
    main()
