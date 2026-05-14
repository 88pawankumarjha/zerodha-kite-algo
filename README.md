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

## Live Order Guard

Live orders require all of these in `.env`:

```bash
DRY_RUN=false
LIVE_TRADING_ENABLED=true
CONFIRM_LIVE_ORDER=I_UNDERSTAND
```

Keep strategy signals separate from order execution. Use Kite instruments data for current `lot_size`, `instrument_token`, expiry, and tick size instead of hardcoding lot sizes.
