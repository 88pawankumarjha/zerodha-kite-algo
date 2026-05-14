from __future__ import annotations

import argparse
import json

from kiteconnect import KiteConnect

from .config import load_settings
from .kite_client import build_kite_client


def build_order_payload(args: argparse.Namespace) -> dict:
    settings = load_settings()
    return {
        "variety": settings.default_variety,
        "exchange": args.exchange or settings.default_exchange,
        "tradingsymbol": args.symbol,
        "transaction_type": args.side,
        "quantity": args.quantity,
        "product": args.product or settings.default_product,
        "order_type": KiteConnect.ORDER_TYPE_LIMIT,
        "price": args.price,
        "validity": settings.default_validity,
        "tag": settings.default_tag,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Place or dry-run a Zerodha Kite LIMIT order.")
    parser.add_argument("--symbol", required=True, help="NFO tradingsymbol, for example NIFTY...")
    parser.add_argument("--quantity", required=True, type=int)
    parser.add_argument("--price", required=True, type=float)
    parser.add_argument("--side", required=True, choices=["BUY", "SELL"])
    parser.add_argument("--exchange", default=None)
    parser.add_argument("--product", default=None)
    args = parser.parse_args()

    settings = load_settings()
    payload = build_order_payload(args)

    if not settings.can_place_live_orders:
        print(json.dumps({"dry_run": True, "order": payload}, indent=2))
        return

    kite = build_kite_client()
    variety = payload.pop("variety")
    response = kite.place_order(variety=variety, **payload)
    print(json.dumps({"dry_run": False, "response": response}, indent=2))


if __name__ == "__main__":
    main()
