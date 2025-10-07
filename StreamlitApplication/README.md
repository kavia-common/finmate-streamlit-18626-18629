# FinMate — Streamlit Personal Finance Assistant

FinMate is a monolithic Streamlit app to help you plan and track your personal finances. Input your income, city, expenses, risk profile, and goals; analyze budgets and projections; get recommendations; and export polished PDF reports. All data is stored locally (offline).

## Key Features
- Multi-page navigation via sidebar:
  - Dashboard: KPIs, quick actions, progress overview
  - Inputs: Profile, city, income, expense categories (editable table)
  - Goals: Create/track goals with current/target amounts and target dates
  - Analytics: KPIs, budget breakdown, cost-of-living adjusted guidance, retirement projection, recommendations, and charts
  - Reports: View saved analysis snapshots and generate PDF reports
  - Settings: Preferences (currency, EF months, real return), data export/import, data reset
- Local JSON data with schema versioning and simple migration
- Charts (Altair) for cashflow, category spending, and projections
- PDF reports (ReportLab) with metrics, allocations, and recommendations
- Works completely offline; no external APIs required

## Getting Started
1. (Optional) Create and activate a virtual environment.
2. Install dependencies:
   pip install -r app/requirements.txt
3. Run the app (binds to 0.0.0.0:3000 by default):
   ./start.sh
   # or equivalently:
   # STREAMLIT_PORT=3000 streamlit run app/app.py --server.address=0.0.0.0 --server.port=3000 --server.headless=true
4. Open the app in your browser at http://localhost:3000 and use the sidebar to navigate among pages.

## Environment Variables
- REPORT_AUTHOR (optional): Sets author metadata for generated PDFs.

## Data Storage
- Local JSON state: app/data/state.json
- Exports: timestamped JSON files in app/data/
- PDF reports: app/reports/

Note: app/data/.gitignore prevents committing your local data.

## Acceptance Criteria Coverage
- Sidebar pages: Dashboard, Inputs, Goals, Analytics, Reports, Settings
- Persistent JSON across reloads with schema version
- Analytics with charts and KPIs, recommendations updated by input
- PDF report generation including allocations and recommendations
- Offline functionality with seeded defaults
