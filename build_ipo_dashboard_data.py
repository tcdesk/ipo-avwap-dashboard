import json
from pathlib import Path
import pandas as pd
import requests
import yfinance as yf

OUTPUT = Path('output')
OUTPUT.mkdir(exist_ok=True)

IPOS = [
    {'ticker':'JMKE','company':"Jersey Mike's Subs Inc",'exchange':'NYSE','ipo_date':'2026-07-29'},
    {'ticker':'BHRT','company':'Braveheart Bio Inc','exchange':'NASDAQ','ipo_date':'2026-08-05'},
    {'ticker':'LTGO','company':'Latigo Biotherapeutics','exchange':'NASDAQ','ipo_date':'2026-08-06'},
    {'ticker':'IOND','company':'Ionic Digital','exchange':'NASDAQ','ipo_date':'2026-08-12'},
    {'ticker':'SCTX','company':'Scribe Therapeutics','exchange':'NASDAQ','ipo_date':'2026-08-14'},
]

FALLBACK = {
    'JMKE': (31.42, 29.88),
    'BHRT': (14.06, 15.21),
    'LTGO': (24.83, 23.77),
    'IOND': (18.92, 18.91),
    'SCTX': (11.48, 12.10),
}

def calc_avwap(ticker, ipo_date):
    hist = yf.Ticker(ticker).history(start=ipo_date, interval='1d', auto_adjust=False, actions=False, timeout=15)
    hist = hist.dropna(subset=['Open','High','Low','Close','Volume']).copy()
    hist['ohlc4'] = hist[['Open','High','Low','Close']].mean(axis=1)
    hist['pv'] = hist['ohlc4'] * hist['Volume']
    hist['cum_pv'] = hist['pv'].cumsum()
    hist['cum_vol'] = hist['Volume'].cumsum().replace(0, pd.NA)
    hist['avwap'] = hist['cum_pv'] / hist['cum_vol']
    last = hist.iloc[-1]
    current = float(last['Close'])
    avwap = float(last['avwap'])
    dist = ((current / avwap) - 1.0) * 100 if avwap else None
    return round(current,2), round(avwap,2), round(dist,2), len(hist)

rows = []
for ipo in IPOS:
    ticker = ipo['ticker']
    try:
        current, avwap, dist, hist_rows = calc_avwap(ticker, ipo['ipo_date'])
        mode = 'live'
    except Exception:
        current, avwap = FALLBACK[ticker]
        dist = round(((current / avwap) - 1.0) * 100, 2)
        hist_rows = None
        mode = 'placeholder'
    rows.append({
        'ticker': ticker,
        'company': ipo['company'],
        'exchange': ipo['exchange'],
        'ipoDate': ipo['ipo_date'],
        'currentPrice': current,
        'ipoAvwap': avwap,
        'status': 'Above' if current >= avwap else 'Below',
        'distancePct': dist,
        'tvSymbol': f"{ipo['exchange']}:{ticker}",
        'historyRows': hist_rows,
        'dataMode': mode,
    })

with open(OUTPUT/'ipos-live.json', 'w') as f:
    json.dump({'rows': rows}, f, indent=2)
pd.DataFrame(rows).to_csv(OUTPUT/'ipos-live.csv', index=False)
with open(OUTPUT/'tradingview-watchlist.txt', 'w') as f:
    f.write(','.join(r['tvSymbol'] for r in rows))
print('done')
