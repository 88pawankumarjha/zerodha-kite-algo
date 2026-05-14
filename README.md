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

For a short option trade, use the short wrapper. It sells the option with a LIMIT order, waits for the sell entry to complete, then places the protective BUY SL-LIMIT order with a 20% stop loss.

```bash
./sell20 SENSEX2651475400CE 20 15
```

With sell price `15`, the BUY stop loss is trigger `18` and limit `18.05`.

After the MIS intraday cutoff, pass `NRML` as the fourth argument:

```bash
./sell20 SENSEX2651475400CE 20 15 NRML
```

The longer command also works when you want a custom stop loss:

```bash
python -m src.sell_option_with_sl --exchange BFO --symbol SENSEX2651475400CE --qty 20 --sell 15 --sl 18
```

## Option Buy With Sell SL

For a long option trade, use the matching buy wrapper. It buys the option with a LIMIT order, waits for the buy entry to complete, then places the protective SELL SL-LIMIT order with a 20% stop loss.

```bash
./buy20 SENSEX2651475400CE 20 15
```

With buy price `15`, the SELL stop loss is trigger `12` and limit `11.95`.

After the MIS intraday cutoff, pass `NRML` as the fourth argument:

```bash
./buy20 SENSEX2651475400CE 20 15 NRML
```

In live mode, automatic stop loss is calculated from the actual executed average price, not just the submitted limit price.

## Live Order Guard

Live orders require all of these in `.env`:

```bash
DRY_RUN=false
LIVE_TRADING_ENABLED=true
CONFIRM_LIVE_ORDER=I_UNDERSTAND
```

Keep strategy signals separate from order execution. Use Kite instruments data for current `lot_size`, `instrument_token`, expiry, and tick size instead of hardcoding lot sizes.
