from __future__ import annotations

import csv
from pathlib import Path

from .kite_client import build_kite_client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NFO_CACHE = PROJECT_ROOT / "data" / "nfo_instruments.csv"


def refresh_nfo_instruments() -> None:
    kite = build_kite_client()
    instruments = kite.instruments("NFO")
    NFO_CACHE.parent.mkdir(parents=True, exist_ok=True)

    with NFO_CACHE.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(instruments[0].keys()) if instruments else []
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(instruments)

    print(f"Saved {len(instruments)} NFO instruments to {NFO_CACHE}")


if __name__ == "__main__":
    refresh_nfo_instruments()
