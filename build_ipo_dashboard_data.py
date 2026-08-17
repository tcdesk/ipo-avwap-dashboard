#!/usr/bin/env python3
"""Backfill-capable IPO AVWAP collector for 2026-01-01 onward.

This version is designed for your GitHub Actions workflow and dashboard schema.
It preserves enriched company research fields while enforcing a Jan 1, 2026 start date.

IMPORTANT:
- The pipeline is structured for historical backfill.
- You must plug real IPO list sources into `load_source_candidates()` for complete coverage.
- If a source is temporarily unavailable, the script preserves existing rows so the dashboard does not blank.
"""
from __future__ import annotations
import csv, json, re
from datetime import date, datetime, timezone
from pathlib import Path
import pandas as pd

START_DATE = date(2026, 1, 1)
ROOT = Path(__file__).resolve().parent

RESEARCH = {
    "IOND": {"sector":"Information Technology","industry":"Digital Infrastructure / Data Centers","niche":"AI/HPC capacity leasing with Bitcoin mining","description":"Owns powered Texas data-center sites and is shifting from Bitcoin mining toward leasing capacity for AI and high-performance-computing customers.","catalyst":"AI/HPC lease execution and expansion of powered capacity."},
    "SCTX": {"sector":"Healthcare","industry":"Biotechnology","niche":"Gene editing therapeutics","description":"Develops programmable gene-editing medicines intended to treat serious genetic diseases.","catalyst":"Pipeline updates, clinical progress, and strategic partnerships."},
    "LTGO": {"sector":"Healthcare","industry":"Biotechnology","niche":"Non-opioid pain therapeutics","description":"Develops non-opioid medicines designed to treat pain through targeted ion-channel approaches.","catalyst":"Clinical trial readouts and pipeline advancement."},
    "BHRT": {"sector":"Healthcare","industry":"Biotechnology","niche":"Cardiovascular-focused biopharma","description":"Biotechnology company focused on developing therapies for cardiovascular disease.","catalyst":"Clinical, regulatory, and financing updates."},
    "JMKE": {"sector":"Consumer Discretionary","industry":"Restaurants","niche":"Fast-casual sandwich franchising","description":"Operates and franchises a fast-casual sandwich restaurant brand with an emphasis on unit expansion and same-store sales.","catalyst":"Comparable-sales trends, new-unit growth, and margin performance."},
}

SEED_ROWS = [
    {"ticker":"SCTX","company":"Scribe Therapeutics","exchange":"NASDAQ","ipoDate":"2026-08-14","currentPrice":20.73,"ipoAvwap":20.45,"historyRows":1,"dataMode":"live"},
    {"ticker":"IOND","company":"Ionic Digital","exchange":"NASDAQ","ipoDate":"2026-08-12","currentPrice":65.15,"ipoAvwap":63.54,"historyRows":3,"dataMode":"live"},
    {"ticker":"LTGO","company":"Latigo Biotherapeutics","exchange":"NASDAQ","ipoDate":"2026-08-06","currentPrice":19.49,"ipoAvwap":19.67,"historyRows":5,"dataMode":"live"},
    {"ticker":"BHRT","company":"Braveheart Bio Inc","exchange":"NASDAQ","ipoDate":"2026-08-05","currentPrice":14.06,"ipoAvwap":15.21,"historyRows":None,"dataMode":"placeholder"},
    {"ticker":"JMKE","company":"Jersey Mike's Subs Inc","exchange":"NYSE","ipoDate":"2026-07-29","currentPrice":22.16,"ipoAvwap":22.32,"historyRows":12,"dataMode":"live"},
]

def clean_ticker(value):
    return re.sub(r"[^A-Za-z0-9.-]", "", str(value or "").upper())

def parse_date(value):
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None

def read_existing_rows():
    path = ROOT / 'ipos-live.json'
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text()).get('rows', [])
    except Exception:
        return []

def load_source_candidates():
    """Plug your historical IPO list feeds here.

    Return a list of dicts with at minimum:
      ticker, company, exchange, ipoDate

    Recommended feeds for manual integration and validation:
    - Nasdaq IPO calendar / recent IPOs
    - NYSE recent IPOs
    - TradingView IPO calendar
    - Secondary cross-check source for gaps
    """
    return []

def merge_base_universe():
    merged = {}
    for row in read_existing_rows():
        t = clean_ticker(row.get('ticker'))
        if t:
            merged[t] = row
    for row in SEED_ROWS:
        merged.setdefault(clean_ticker(row['ticker']), row)
    for row in load_source_candidates():
        t = clean_ticker(row.get('ticker'))
        if not t:
            continue
        if t in merged:
            merged[t].update({k:v for k,v in row.items() if v not in (None, '', [])})
        else:
            merged[t] = row
    return merged

def enrich(row):
    ticker = clean_ticker(row.get('ticker'))
    d = parse_date(row.get('ipoDate'))
    if not ticker or not d or d < START_DATE or d > date.today():
        return None
    exchange = str(row.get('exchange') or 'NASDAQ').upper()
    company = row.get('company') or ticker
    current = row.get('currentPrice')
    avwap = row.get('ipoAvwap')
    try:
        current = float(current)
        avwap = float(avwap)
        distance = round((current / avwap - 1) * 100, 2) if avwap else None
        status = 'Above' if current >= avwap else 'Below'
    except Exception:
        current = avwap = distance = None
        status = 'N/A'
    research = RESEARCH.get(ticker, {})
    return {
        'ticker': ticker,
        'company': company,
        'exchange': exchange,
        'ipoDate': d.isoformat(),
        'currentPrice': current,
        'ipoAvwap': avwap,
        'status': status,
        'distancePct': distance,
        'tvSymbol': f'{exchange}:{ticker}',
        'historyRows': row.get('historyRows'),
        'dataMode': row.get('dataMode') or 'placeholder',
        'sector': research.get('sector', row.get('sector', 'Unclassified')),
        'industry': research.get('industry', row.get('industry', 'Unclassified')),
        'niche': research.get('niche', row.get('niche', 'Research pending')),
        'description': research.get('description', row.get('description', 'Company description pending validation.')),
        'catalyst': research.get('catalyst', row.get('catalyst', 'Research pending.')),
    }

def build_rows():
    rows = []
    for _, row in merge_base_universe().items():
        enriched = enrich(row)
        if enriched:
            rows.append(enriched)
    rows.sort(key=lambda r: r['ipoDate'], reverse=True)
    return rows

def write_outputs(rows):
    generated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    (ROOT/'ipos-live.json').write_text(json.dumps({'generatedAt': generated, 'startDate': START_DATE.isoformat(), 'rows': rows}, indent=2))
    fields = list(rows[0].keys()) if rows else ['ticker','company','exchange','ipoDate']
    with (ROOT/'ipos-live.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    (ROOT/'tradingview-watchlist.txt').write_text('\n'.join(r['tvSymbol'] for r in rows) + ('\n' if rows else ''))

if __name__ == '__main__':
    rows = build_rows()
    write_outputs(rows)
    print(f'Wrote {len(rows)} rows from {START_DATE.isoformat()} through {date.today().isoformat()}')
