from __future__ import annotations

import argparse
import json
import time
from typing import Any

from kiteconnect import KiteConnect

from .config import load_settings
from .kite_client import build_kite_client


TERMINAL_FAILURE_STATUSES = {"REJECTED", "CANCELLED"}


def round_to_tick(value: float, tick_size: float) -> float:
    return round(round(value / tick_size) * tick_size, 2)


def build_entry_payload(args: argparse.Namespace) -> dict[str, Any]:
    settings = load_settings()
    return {
        "variety": settings.default_variety,
        "exchange": args.exchange or settings.default_exchange,
        "tradingsymbol": args.symbol,
        "transaction_type": KiteConnect.TRANSACTION_TYPE_SELL,
        "quantity": args.quantity,
        "product": args.product or settings.default_product,
        "order_type": KiteConnect.ORDER_TYPE_LIMIT,
        "price": args.sell_price,
        "validity": settings.default_validity,
        "tag": settings.default_tag,
    }


def build_stop_loss_payload(args: argparse.Namespace) -> dict[str, Any]:
    settings = load_settings()
    limit_price = args.sl_limit
    if limit_price is None:
        limit_price = round_to_tick(args.sl_trigger + args.tick_size, args.tick_size)

    return {
        "variety": settings.default_variety,
        "exchange": args.exchange or settings.default_exchange,
        "tradingsymbol": args.symbol,
        "transaction_type": KiteConnect.TRANSACTION_TYPE_BUY,
        "quantity": args.quantity,
        "product": args.product or settings.default_product,
        "order_type": KiteConnect.ORDER_TYPE_SL,
        "price": limit_price,
        "trigger_price": args.sl_trigger,
        "validity": settings.default_validity,
        "tag": settings.default_tag,
    }


def validate_prices(entry: dict[str, Any], stop_loss: dict[str, Any]) -> None:
    sell_price = float(entry["price"])
    trigger_price = float(stop_loss["trigger_price"])
    limit_price = float(stop_loss["price"])

    if trigger_price <= sell_price:
        raise ValueError("For option selling, buy SL trigger must be above the sell entry price.")
    if limit_price < trigger_price:
        raise ValueError("For a BUY SL-LIMIT order, limit price must be at or above trigger price.")


def place_order(kite: KiteConnect, payload: dict[str, Any]) -> str:
    request = dict(payload)
    variety = request.pop("variety")
    return kite.place_order(variety=variety, **request)


def wait_for_completion(
    kite: KiteConnect,
    order_id: str,
    timeout_seconds: int,
    poll_seconds: int,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        history = kite.order_history(order_id)
        latest = history[-1] if history else {}
        status = latest.get("status")

        if status == KiteConnect.STATUS_COMPLETE:
            return latest
        if status in TERMINAL_FAILURE_STATUSES:
            raise RuntimeError(f"Entry order {order_id} ended with status {status}: {latest}")

        time.sleep(poll_seconds)

    raise TimeoutError(f"Entry order {order_id} did not complete within {timeout_seconds} seconds.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sell an option with a LIMIT entry, then place a protective BUY SL-LIMIT order."
    )
    parser.add_argument("--symbol", required=True, help="Exchange tradingsymbol, for example SENSEX...")
    parser.add_argument("--quantity", "--qty", required=True, type=int)
    parser.add_argument("--sell-price", "--sell", required=True, type=float)
    parser.add_argument("--sl-trigger", "--sl", required=True, type=float)
    parser.add_argument("--sl-limit", type=float, default=None)
    parser.add_argument("--tick-size", type=float, default=0.05)
    parser.add_argument("--exchange", default=None)
    parser.add_argument("--product", default=None)
    parser.add_argument("--entry-timeout", type=int, default=60)
    parser.add_argument("--poll-seconds", type=int, default=2)
    args = parser.parse_args()

    settings = load_settings()
    entry_payload = build_entry_payload(args)
    stop_loss_payload = build_stop_loss_payload(args)
    validate_prices(entry_payload, stop_loss_payload)

    if not settings.can_place_live_orders:
        print(
            json.dumps(
                {
                    "dry_run": True,
                    "entry": entry_payload,
                    "stop_loss_after_entry_complete": stop_loss_payload,
                },
                indent=2,
            )
        )
        return

    kite = build_kite_client()
    entry_order_id = place_order(kite, entry_payload)
    entry_status = wait_for_completion(kite, entry_order_id, args.entry_timeout, args.poll_seconds)
    stop_loss_order_id = place_order(kite, stop_loss_payload)

    print(
        json.dumps(
            {
                "dry_run": False,
                "entry_order_id": entry_order_id,
                "entry_status": entry_status,
                "stop_loss_order_id": stop_loss_order_id,
                "stop_loss": stop_loss_payload,
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
