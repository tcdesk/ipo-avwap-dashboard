IPO AVWAP dashboard package

Generated: 2026-08-16 17:23 UTC

Files:
- ipo-avwap-dashboard-final.html : final dark-themed dashboard
- ipos-live.json : machine-readable dataset for the dashboard
- ipos-live.csv : spreadsheet-friendly export
- tradingview-watchlist.txt : TradingView import list with exchange-prefixed symbols
- build_ipo_dashboard_data.py : Python collector that recalculates IPO AVWAP using daily OHLCV

AVWAP method reproduced from your Pine logic:
- Anchor at first trading bar after listing
- Source = OHLC4
- AVWAP = cumulative(OHLC4 * volume) / cumulative(volume)
- Status = Above if current close >= IPO AVWAP, otherwise Below

Important:
- Public IPO sources can be incomplete or unavailable on some requests.
- This package includes live-attempt rows plus placeholder fallback rows so the dashboard always renders.
- TradingView watchlist import uses a text list of symbols with exchange prefixes.
