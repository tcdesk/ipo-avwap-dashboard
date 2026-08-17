IPO AVWAP DASHBOARD — PROFESSIONAL RESEARCH UPDATE

Replace these files in the root of your GitHub repository:
1. ipo-avwap-dashboard-final.html
2. ipos-live.json
3. ipos-live.csv
4. tradingview-watchlist.txt

Do NOT replace build_ipo_dashboard_data.py unless you have updated your collector to produce the added company fields.

The dashboard now:
- Removes the old subtitle and yellow package/disclaimer banner.
- Removes the right-side TradingView, Package Files, and AVWAP Rules panels.
- Makes the IPO research table full width.
- Adds Sector, Industry, Niche, and What It Does columns.
- Adds a sector filter and wider research-oriented search.
- Keeps the top-bar CSV and TradingView copy actions.

Deployment:
1. Upload/replace the four files above in GitHub.
2. Commit to main.
3. Go to Actions > Refresh IPO AVWAP Dashboard.
4. Click Run workflow.
5. Wait for the deployment to finish, then hard-refresh the dashboard (Ctrl+F5 on Windows, Cmd+Shift+R on Mac).

For DAILY AUTOMATION:
Update build_ipo_dashboard_data.py so every generated row includes:
sector, industry, niche, description, catalyst
Otherwise, the daily script may overwrite the enriched JSON with a version that omits those fields.
