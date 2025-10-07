# FinMate — Streamlit Personal Finance Assistant

FinMate analyzes user inputs (income, city, goals) and provides personalized recommendations, with options to save sessions and export PDF reports.

## Features
- Interactive UI for inputs
- Financial analysis and smart recommendations
- Local JSON persistence for sessions
- PDF report generation

## Getting Started
1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:
   pip install -r app/requirements.txt
3. Run the app:
   streamlit run app/app.py

## Environment Variables
- REPORT_AUTHOR: Optional. Sets the author metadata for generated PDFs.

You can set these using a .env (depending on your environment setup) or export them before running.

## Data Storage
- Local JSON at app/data/sessions.json
- PDF reports saved in app/reports/
