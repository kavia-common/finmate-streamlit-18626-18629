import os
import streamlit as st
import pandas as pd
from datetime import datetime
from src.analysis import analyze_finances, default_goals
from src.storage import load_sessions, save_session
from src.report import generate_pdf_report
from src.utils import currency, validate_positive_number

st.set_page_config(page_title="FinMate", page_icon="💰", layout="wide")

AUTHOR = os.getenv("REPORT_AUTHOR", "FinMate")

if "sessions" not in st.session_state:
    st.session_state.sessions = load_sessions()

st.title("💰 FinMate — Personal Finance Assistant")
st.caption("Analyze your finances, get smart recommendations, and export a polished PDF report.")

with st.sidebar:
    st.header("User Profile")
    name = st.text_input("Your name", value="")
    city = st.text_input("City", value="")
    income = st.number_input("Monthly Income ($)", min_value=0.0, step=100.0, format="%0.2f")
    expenses = st.number_input("Monthly Expenses ($)", min_value=0.0, step=50.0, format="%0.2f")

    st.markdown("---")
    st.subheader("Goals")
    goal_options = default_goals()
    selected_goals = st.multiselect("Select your goals", goal_options, default=[goal_options[0]])
    horizon_years = st.slider("Planning Horizon (years)", min_value=1, max_value=30, value=5)

    st.markdown("---")
    run = st.button("Analyze 🚀")

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Results")
    if run:
        errors = []
        if not name:
            errors.append("Please enter your name.")
        if income <= 0:
            errors.append("Income must be greater than 0.")
        if expenses < 0:
            errors.append("Expenses cannot be negative.")
        if expenses > income:
            st.info("Your expenses exceed your income. We'll still analyze, but consider expense reductions.")
        if errors:
            st.error("\n".join(errors))
        else:
            analysis = analyze_finances(name=name, city=city, income=income, expenses=expenses, goals=selected_goals, horizon_years=horizon_years)

            st.success("Analysis complete! Review your personalized recommendations below.")

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.metric("Savings Rate", f"{analysis['savings_rate_pct']}%")
            with kpi2:
                st.metric("Monthly Savings", currency(analysis['monthly_savings']))
            with kpi3:
                st.metric("Emergency Fund Target", currency(analysis['emergency_fund_target']))
            with kpi4:
                st.metric("Investment Budget", currency(analysis['investment_budget']))

            st.markdown("### Allocation Suggestions")
            df_alloc = pd.DataFrame([
                {"Bucket": k, "Allocation": v} for k, v in analysis["allocations"].items()
            ])
            st.dataframe(df_alloc, hide_index=True, use_container_width=True)

            st.markdown("### Recommendations")
            for rec in analysis["recommendations"]:
                st.markdown(f"- {rec}")

            st.markdown("---")
            st.subheader("Save & Export")
            session_name = st.text_input("Session label", value=f"{name}-{datetime.now().strftime('%Y%m%d-%H%M')}")
            colA, colB = st.columns([1,1])
            with colA:
                if st.button("Save Session 💾"):
                    payload = {"meta": {"created_at": datetime.now().isoformat()}, "input": {"name": name, "city": city, "income": income, "expenses": expenses, "goals": selected_goals, "horizon_years": horizon_years}, "analysis": analysis}
                    save_session(session_name, payload)
                    st.success("Session saved.")
            with colB:
                if st.button("Export PDF 📄"):
                    pdf_path = generate_pdf_report(session_name=session_name, user_name=name, city=city, income=income, expenses=expenses, analysis=analysis, author=AUTHOR)
                    st.success(f"PDF generated: {pdf_path}")

with col2:
    st.subheader("Saved Sessions")
    sessions = st.session_state.sessions = load_sessions()  # refresh
    if not sessions:
        st.info("No saved sessions yet.")
    else:
        selected = st.selectbox("Select a session to view", options=list(sessions.keys()))
        if selected:
            s = sessions[selected]
            st.json(s)
