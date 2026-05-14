# Zerodha Kite Algo Workspace

This is the Zerodha-only workspace for the options trading bot. It keeps broker credentials out of source control and defaults every order path to dry run.

## Setup

```bash
cd /Users/pawan.kumarjha/sho/zerodha-kite-algo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` locally with the Kite API key and secret. Do not commit `.env`.

## Login

```bash
python -m src.auth_login
```

The script prints the Kite login URL. Open it in the intended personal browser profile, complete login, then paste only the `request_token` value from the redirect URL. The generated access token is stored in `.kite_access_token`, which is ignored by Git.

## Dry Run Order Check

```bash
python -m src.place_limit_order --symbol NIFTY00000CE --quantity 1 --price 1.0 --side BUY
```

This prints the order payload and does not place a live order while `DRY_RUN=true`.

## Stop-Loss Exit Check

For a bought option position, place a protective sell SL-LIMIT order. The trigger is the stop-loss level; the limit price should normally be slightly below the trigger for a sell order so it has room to fill after triggering.

```bash
python -m src.place_stop_loss_order --exchange BFO --symbol SENSEX2651475400CE --quantity 20 --trigger-price 13 --limit-price 12.95 --side SELL
```

## Option Sell With Buy SL

For a short option trade, use one command. It sells the option with a LIMIT order, waits for the sell entry to complete, then places the protective BUY SL-LIMIT order.

```bash
python -m src.sell_option_with_sl --exchange BFO --symbol SENSEX2651475400CE --qty 20 --sell 15 --sl 18
```

If `--sl-limit` is omitted, it defaults to one tick above the trigger. With `--sl 18`, the BUY SL-LIMIT order uses trigger `18` and limit `18.05`.

## Live Order Guard

Live orders require all of these in `.env`:

```bash
DRY_RUN=false
LIVE_TRADING_ENABLED=true
CONFIRM_LIVE_ORDER=I_UNDERSTAND
```

Keep strategy signals separate from order execution. Use Kite instruments data for current `lot_size`, `instrument_token`, expiry, and tick size instead of hardcoding lot sizes.
