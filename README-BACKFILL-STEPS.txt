IPO AVWAP — JAN 2026 HISTORICAL BACKFILL PACKAGE

What this package does
- Sets the dashboard retention window to 2026-01-01 through the current run date.
- Preserves your current working dashboard layout and company-research schema.
- Adds a backfill-capable collector structure that keeps enriched fields on every refresh.
- Prevents a temporary source outage from blanking the dashboard by preserving current rows.

What this package does NOT do automatically
- It does not magically discover every IPO since Jan 2026 unless you feed historical IPO candidates into the collector.
- The provided collector is structured for that backfill but still needs real source rows added to load_source_candidates().

FILES INCLUDED
1. build_ipo_dashboard_data.py
2. ipo-avwap-dashboard-final.html
3. ipos-live.json
4. ipos-live.csv
5. tradingview-watchlist.txt
6. refresh-ipo-dashboard.yml
7. README-BACKFILL-STEPS.txt

INSTALL STEPS
1. Download and unzip this package.
2. In GitHub, replace these ROOT files in your repository:
   - build_ipo_dashboard_data.py
   - ipo-avwap-dashboard-final.html
   - ipos-live.json
   - ipos-live.csv
   - tradingview-watchlist.txt
3. Do NOT upload refresh-ipo-dashboard.yml to the repository root if you already have the workflow inside .github/workflows/.
4. If your existing workflow file inside .github/workflows/refresh-ipo-dashboard.yml is working, keep it.
5. Commit the file replacements to main.
6. Go to Actions > Refresh IPO AVWAP Dashboard > Run workflow.
7. After the workflow finishes, hard-refresh the site.

HOW TO ACTUALLY LOAD ALL IPOs SINCE JAN 2026
You now need to populate the collector's load_source_candidates() function with historical IPO rows.
Each row should include at least:
  ticker, company, exchange, ipoDate
Optional fields:
  currentPrice, ipoAvwap, historyRows, dataMode, sector, industry, niche, description, catalyst

Suggested workflow for backfill:
A. Build a historical candidate list from Jan 1, 2026 onward.
B. Add the candidate rows into load_source_candidates() or an external source file.
C. Run the collector locally or via GitHub Actions.
D. Review the resulting ipos-live.json.
E. Expand the RESEARCH dictionary for names missing sector/industry/niche/description/catalyst.

IMPORTANT
The dashboard can only show what exists in ipos-live.json.
Changing the date window alone does not expand the universe.
The universe expands only when the collector is fed more IPO candidates.
