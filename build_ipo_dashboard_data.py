#!/usr/bin/env python3
"""Build IPO AVWAP dashboard data for US IPOs from 2026-01-01 onward."""
from __future__ import annotations
import csv, json, os, re
from datetime import date, datetime, timezone
from pathlib import Path
import pandas as pd

START_DATE = date(2026, 1, 1)
ROOT = Path(__file__).resolve().parent

# This file is your durable research layer. Add/edit records as you validate names.
# The collector preserves these fields on every scheduled refresh.
RESEARCH = {
    "IOND": {"sector":"Information Technology","industry":"Digital Infrastructure / Data Centers","niche":"AI/HPC capacity leasing with Bitcoin mining","description":"Owns powered Texas data-center sites and is shifting from Bitcoin mining toward leasing capacity for AI and high-performance-computing customers.","catalyst":"AI/HPC lease execution and expansion of powered capacity."},
    "SCTX": {"sector":"Healthcare","industry":"Biotechnology","niche":"Gene editing therapeutics","description":"Develops programmable gene-editing medicines intended to treat serious genetic diseases.","catalyst":"Pipeline updates, clinical progress, and strategic partnerships."},
    "LTGO": {"sector":"Healthcare","industry":"Biotechnology","niche":"Non-opioid pain therapeutics","description":"Develops non-opioid medicines designed to treat pain through targeted ion-channel approaches.","catalyst":"Clinical trial readouts and pipeline advancement."},
    "BHRT": {"sector":"Healthcare","industry":"Biotechnology","niche":"Cardiovascular-focused biopharma","description":"Biotechnology company focused on developing therapies for cardiovascular disease.","catalyst":"Clinical, regulatory, and financing updates."},
    "JMKE": {"sector":"Consumer Discretionary","industry":"Restaurants","niche":"Fast-casual sandwich franchising","description":"Operates and franchises a fast-casual sandwich restaurant brand with an emphasis on unit expansion and same-store sales.","catalyst":"Comparable-sales trends, new-unit growth, and margin performance."},
}

FALLBACK_ROWS = [
    {"ticker":"SCTX","company":"Scribe Therapeutics","exchange":"NASDAQ","ipoDate":"2026-08-14"},
    {"ticker":"IOND","company":"Ionic Digital","exchange":"NASDAQ","ipoDate":"2026-08-12"},
    {"ticker":"LTGO","company":"Latigo Biotherapeutics","exchange":"NASDAQ","ipoDate":"2026-08-06"},
    {"ticker":"BHRT","company":"Braveheart Bio Inc","exchange":"NASDAQ","ipoDate":"2026-08-05"},
    {"ticker":"JMKE","company":"Jersey Mike's Subs Inc","exchange":"NYSE","ipoDate":"2026-07-29"},
]

def clean_ticker(value):
    value = re.sub(r"[^A-Za-z0-9.-]", "", str(value or "").upper())
    return value if 1 <= len(value) <= 8 else ""

def normalize_date(value):
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None

def read_existing():
    path = ROOT / "ipos-live.json"
    if not path.exists(): return []
    try: return json.loads(path.read_text()).get("rows", [])
    except Exception: return []

def collect_rows():
    # This preserves the stable current dataset; extend this function with paid/free IPO sources.
    # A source failure must not erase the dashboard on a scheduled run.
    existing = read_existing()
    merged = {clean_ticker(r.get("ticker")): r for r in existing if clean_ticker(r.get("ticker"))}
    for r in FALLBACK_ROWS: merged.setdefault(r["ticker"], r)
    output=[]
    for ticker, r in merged.items():
        d = normalize_date(r.get("ipoDate"))
        if not d or d < START_DATE or d > date.today(): continue
        exchange = str(r.get("exchange") or "NASDAQ").upper()
        research = RESEARCH.get(ticker, {})
        current = r.get("currentPrice")
        avwap = r.get("ipoAvwap")
        try:
            current, avwap = float(current), float(avwap)
            distance = round((current / avwap - 1) * 100, 2) if avwap else None
            status = "Above" if current >= avwap else "Below"
        except Exception:
            current=avwap=distance=None; status="N/A"
        output.append({
            "ticker":ticker, "company":r.get("company") or ticker, "exchange":exchange,
            "ipoDate":d.isoformat(), "currentPrice":current, "ipoAvwap":avwap,
            "status":status, "distancePct":distance, "tvSymbol":f"{exchange}:{ticker}",
            "historyRows":r.get("historyRows"), "dataMode":r.get("dataMode") or "placeholder",
            "sector":research.get("sector", r.get("sector", "Unclassified")),
            "industry":research.get("industry", r.get("industry", "Unclassified")),
            "niche":research.get("niche", r.get("niche", "Research pending")),
            "description":research.get("description", r.get("description", "Company description pending validation.")),
            "catalyst":research.get("catalyst", r.get("catalyst", "Research pending.")),
        })
    return sorted(output, key=lambda x:x["ipoDate"], reverse=True)

def write_outputs(rows):
    generated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    (ROOT/"ipos-live.json").write_text(json.dumps({"generatedAt":generated,"startDate":START_DATE.isoformat(),"rows":rows}, indent=2))
    fields=list(rows[0].keys()) if rows else ["ticker","company","exchange","ipoDate"]
    with (ROOT/"ipos-live.csv").open("w", newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    (ROOT/"tradingview-watchlist.txt").write_text("\n".join(r["tvSymbol"] for r in rows)+"\n")

if __name__ == "__main__":
    rows=collect_rows(); write_outputs(rows)
    print(f"Wrote {len(rows)} IPO rows from {START_DATE.isoformat()} through {date.today().isoformat()}")
