import os
from datetime import datetime, date
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from src.analysis import (
    analyze_finances,
    default_goals,
    compute_budget_breakdown,
    retirement_projection,
    build_recommendations,
    goal_progress_summary,
)
from src.models import UserProfile, ExpenseItem, Goal, AppState
from src.report import generate_pdf_report
from src.storage import (
    load_app_state,
    save_app_state,
    export_state_json,
    import_state_json,
    reset_app_state,
)
from src.utils import (
    currency,
    CITY_COL_INDEX,
    col_index_for_city,
    months_of_expense_coverage,
    with_cache_df,
)

st.set_page_config(page_title="FinMate", page_icon="💰", layout="wide")

AUTHOR = os.getenv("REPORT_AUTHOR", "FinMate")

# Initialize state
if "state" not in st.session_state:
    st.session_state.state = load_app_state()

state: AppState = st.session_state.state

# Sidebar Navigation
with st.sidebar:
    st.title("FinMate")
    page = st.radio(
        "Navigate",
        options=["Dashboard", "Inputs", "Goals", "Analytics", "Reports", "Settings"],
        index=0,
    )
    st.markdown("---")
    st.caption("Local data is stored offline in app/data/")

def save_state_and_notify():
    save_app_state(st.session_state.state)
    st.toast("Saved", icon="💾")

# Dashboard Page
def page_dashboard():
    st.title("💰 FinMate — Personal Finance Assistant")
    st.caption("Track KPIs at a glance and jump to quick actions.")

    profile = state.user
    exp_total = sum(x.amount for x in state.expenses)
    net_monthly = max(profile.income - exp_total, 0.0)
    savings_rate = 0.0 if profile.income <= 0 else (net_monthly / profile.income)
    ef_target = exp_total * state.settings.emergency_fund_months
    ef_current = state.settings.emergency_fund_current
    ef_coverage = months_of_expense_coverage(ef_current, exp_total)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Net Monthly", currency(net_monthly))
    with k2:
        st.metric("Savings Rate", f"{round(savings_rate*100,1)}%")
    with k3:
        st.metric("Emergency Fund Coverage", f"{round(ef_coverage,1)} months")
    with k4:
        progress_txt, progress_pct = goal_progress_summary(state.goals)
        st.metric("Goals Progress", f"{progress_pct}%")
        st.caption(progress_txt)

    st.markdown("---")
    st.subheader("Quick Actions")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Add Expense Category ➕"):
            st.session_state._nav_to = "Inputs"
    with c2:
        if st.button("Add Goal 🎯"):
            st.session_state._nav_to = "Goals"
    with c3:
        if st.button("Run Analysis 🚀"):
            st.session_state._nav_to = "Analytics"

    # Recent Sessions/State summary
    st.markdown("### Summary")
    st.json(
        {
            "name": profile.name,
            "city": profile.city,
            "income": profile.income,
            "expense_total": exp_total,
            "goals_count": len(state.goals),
        }
    )

# Inputs Page
def page_inputs():
    st.title("Inputs")
    st.caption("Provide your core financial info and monthly expenses.")

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name", value=state.user.name)
            city = st.text_input("City", value=state.user.city)
            age = st.number_input("Age", min_value=0, max_value=120, value=state.user.age)
        with c2:
            income = st.number_input(
                "Monthly Income",
                min_value=0.0,
                step=100.0,
                value=state.user.income,
                format="%0.2f",
            )
            risk = st.selectbox(
                "Risk Profile",
                options=["Conservative", "Balanced", "Aggressive"],
                index=["Conservative", "Balanced", "Aggressive"].index(state.user.risk_profile),
            )

        st.markdown("#### Monthly Expenses")
        if len(state.expenses) == 0:
            # seed with some defaults
            for nm in ["Housing", "Food", "Transport", "Utilities", "Discretionary"]:
                state.expenses.append(ExpenseItem(category=nm, amount=0.0))

        exp_df = pd.DataFrame(
            [{"Category": e.category, "Amount": e.amount} for e in state.expenses]
        )
        edited = st.data_editor(
            exp_df,
            num_rows="dynamic",
            use_container_width=True,
            key="exp_editor",
        )

        submitted = st.form_submit_button("Save Profile & Expenses 💾")
        if submitted:
            # validate
            if income < 0:
                st.error("Income must be >= 0")
                return
            bad = edited[edited["Amount"] < 0]
            if not bad.empty:
                st.error("Expense amounts must be >= 0")
                return

            # persist
            state.user = UserProfile(
                name=name, city=city, age=int(age), income=float(income), risk_profile=risk
            )
            # dedupe and rebuild expenses
            new_exp: List[ExpenseItem] = []
            for _, row in edited.iterrows():
                cat = str(row["Category"]).strip()
                if not cat:
                    continue
                amt = float(row["Amount"])
                new_exp.append(ExpenseItem(category=cat, amount=amt))
            state.expenses = new_exp
            save_state_and_notify()

    st.markdown("#### City Cost-of-Living Index")
    c = col_index_for_city(state.user.city)
    st.info(f"COL index for '{state.user.city or 'N/A'}': {c:.2f} (1.00 = baseline)")

# Goals Page
def page_goals():
    st.title("Goals")
    st.caption("Manage your financial goals and track progress.")

    # Goals CRUD
    with st.form("goals_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Goal Name")
        with c2:
            target_amount = st.number_input(
                "Target Amount", min_value=0.0, step=100.0, value=0.0, format="%0.2f"
            )
        with c3:
            target_date = st.date_input("Target Date", value=date.today())
        current_amount = st.number_input(
            "Current Amount", min_value=0.0, step=100.0, value=0.0, format="%0.2f"
        )
        add = st.form_submit_button("Add Goal")
        if add:
            if not name.strip():
                st.error("Goal name is required")
            else:
                state.goals.append(
                    Goal(
                        name=name.strip(),
                        target_amount=target_amount,
                        target_date=str(target_date),
                        current_amount=current_amount,
                    )
                )
                save_state_and_notify()

    if len(state.goals) == 0:
        st.info("No goals yet. Add your first goal above.")
        return

    # Editable goals table
    df = pd.DataFrame([g.dict() for g in state.goals])
    df["target_date"] = pd.to_datetime(df["target_date"]).dt.date
    edited = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, key="goals_editor"
    )
    if st.button("Save Goals 💾"):
        new: List[Goal] = []
        for _, r in edited.iterrows():
            nm = str(r["name"]).strip()
            if not nm:
                continue
            new.append(
                Goal(
                    name=nm,
                    target_amount=float(r["target_amount"]),
                    target_date=str(r["target_date"]),
                    current_amount=float(r.get("current_amount", 0.0)),
                )
            )
        state.goals = new
        save_state_and_notify()

# Analytics Page
def page_analytics():
    st.title("Analytics")
    st.caption("Visualize your cashflow, spending, and projections.")

    profile = state.user
    exp_total = sum(x.amount for x in state.expenses)
    if profile.income <= 0 and exp_total <= 0:
        st.info("Please enter your income and expenses on the Inputs page.")
        return

    # Core analysis
    analysis = analyze_finances(
        name=profile.name,
        city=profile.city,
        income=profile.income,
        expenses=exp_total,
        goals=[g.name for g in state.goals] or default_goals(),
        horizon_years=max(1, state.settings.retirement_horizon_years),
        risk_profile=profile.risk_profile,
        emergency_fund_current=state.settings.emergency_fund_current,
        emergency_fund_months=state.settings.emergency_fund_months,
    )
    recos = build_recommendations(analysis, state)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Savings Rate", f"{analysis['savings_rate_pct']}%")
    with k2:
        st.metric("Monthly Savings", currency(analysis["monthly_savings"]))
    with k3:
        st.metric("Emergency Fund Target", currency(analysis["emergency_fund_target"]))
    with k4:
        st.metric("Investment Budget", currency(analysis["investment_budget"]))

    # Charts
    st.markdown("### Charts")
    import altair as alt

    # Monthly cashflow (income vs expenses)
    cf_df = pd.DataFrame(
        [
            {"Type": "Income", "Amount": profile.income},
            {"Type": "Expenses", "Amount": exp_total},
            {"Type": "Savings", "Amount": max(profile.income - exp_total, 0.0)},
        ]
    )
    cf_chart = (
        alt.Chart(cf_df)
        .mark_bar()
        .encode(x="Type", y="Amount:Q", color="Type")
        .properties(height=240)
    )
    st.altair_chart(cf_chart, use_container_width=True)

    # Expense by category
    cat_df = pd.DataFrame([{"Category": e.category, "Amount": e.amount} for e in state.expenses])
    cat_chart = (
        alt.Chart(cat_df)
        .mark_bar()
        .encode(x="Category:N", y="Amount:Q", color="Category")
        .properties(height=260)
    )
    st.altair_chart(cat_chart, use_container_width=True)

    # Retirement projection
    rp_df = retirement_projection(
        monthly_invest=analysis["allocations"].get("Investments", 0.0),
        years=max(1, state.settings.retirement_horizon_years),
        real_return=state.settings.real_return_assumption,
    )
    rp_chart = (
        alt.Chart(rp_df)
        .mark_line(point=True)
        .encode(x="Year:O", y="Balance:Q")
        .properties(height=260, title="Retirement Projection (real)")
    )
    st.altair_chart(rp_chart, use_container_width=True)

    st.markdown("### Allocation Suggestions")
    df_alloc = pd.DataFrame(
        [{"Bucket": k, "Allocation": v} for k, v in analysis["allocations"].items()]
    )
    st.dataframe(df_alloc, hide_index=True, use_container_width=True)

    st.markdown("### Recommendations")
    for rec in recos:
        st.markdown(f"- {rec}")

    # Save & Export
    st.markdown("---")
    st.subheader("Save & Export")
    default_label = f"{profile.name or 'session'}-{datetime.now().strftime('%Y%m%d-%H%M')}"
    session_name = st.text_input("Session label", value=default_label)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save Snapshot 💾"):
            payload = {
                "meta": {"created_at": datetime.now().isoformat()},
                "input": {
                    "name": profile.name,
                    "city": profile.city,
                    "income": profile.income,
                    "expenses": exp_total,
                    "goals": [g.name for g in state.goals],
                    "horizon_years": state.settings.retirement_horizon_years,
                },
                "analysis": analysis,
            }
            # store in state.session_history
            state.sessions[session_name] = payload
            save_state_and_notify()
            st.success("Snapshot saved.")
    with c2:
        if st.button("Export PDF 📄"):
            pdf_path = generate_pdf_report(
                session_name=session_name,
                user_name=profile.name,
                city=profile.city,
                income=profile.income,
                expenses=exp_total,
                analysis=analysis,
                author=AUTHOR,
            )
            st.success(f"PDF generated: {pdf_path}")

# Reports Page
def page_reports():
    st.title("Reports")
    st.caption("Browse saved analysis snapshots and download PDFs.")

    if not state.sessions:
        st.info("No saved snapshots yet.")
        return

    keys = list(state.sessions.keys())
    selected = st.selectbox("Select a snapshot", options=keys)
    s = state.sessions.get(selected)
    if s:
        st.json(s)
        if st.button("Generate PDF 📄"):
            pdf_path = generate_pdf_report(
                session_name=selected,
                user_name=s["input"]["name"],
                city=s["input"]["city"],
                income=s["input"]["income"],
                expenses=s["input"]["expenses"],
                analysis=s["analysis"],
                author=AUTHOR,
            )
            st.success(f"PDF generated: {pdf_path}")

# Settings Page
def page_settings():
    st.title("Settings")
    st.caption("Manage data and preferences.")

    st.subheader("Preferences")
    c1, c2, c3 = st.columns(3)
    with c1:
        currency_symbol = st.text_input(
            "Currency Symbol", value=state.settings.currency_symbol
        )
    with c2:
        emergency_fund_months = st.slider(
            "Emergency Fund Months", min_value=1, max_value=12, value=state.settings.emergency_fund_months
        )
    with c3:
        real_return = st.number_input(
            "Real Return Assumption (annual, %)",
            min_value=0.0,
            max_value=15.0,
            value=state.settings.real_return_assumption * 100,
            step=0.5,
            format="%.1f",
        )

    st.subheader("Emergency Fund")
    ef_c1, ef_c2 = st.columns(2)
    with ef_c1:
        ef_current = st.number_input(
            "Current EF Amount",
            min_value=0.0,
            value=state.settings.emergency_fund_current,
            step=100.0,
            format="%0.2f",
        )
    with ef_c2:
        st.caption("Saved for emergencies; used to compute coverage months.")

    if st.button("Save Settings 💾"):
        state.settings.currency_symbol = currency_symbol or "$"
        state.settings.emergency_fund_months = int(emergency_fund_months)
        state.settings.real_return_assumption = float(real_return) / 100.0
        state.settings.emergency_fund_current = ef_current
        save_state_and_notify()

    st.markdown("---")
    st.subheader("Data Management")
    d1, d2, d3 = st.columns(3)
    with d1:
        if st.button("Export JSON ⬇️"):
            path = export_state_json()
            st.success(f"Exported to {path}")
    with d2:
        uploaded = st.file_uploader("Import JSON ⬆️", type=["json"])
        if uploaded is not None and st.button("Import Now"):
            ok, msg = import_state_json(uploaded)
            if ok:
                st.success("Imported successfully.")
                st.session_state.state = load_app_state()
            else:
                st.error(f"Import failed: {msg}")
    with d3:
        if st.button("Reset Data ♻️"):
            reset_app_state()
            st.session_state.state = load_app_state()
            st.success("Data reset to defaults.")

# Router
if page == "Dashboard":
    page_dashboard()
elif page == "Inputs":
    page_inputs()
elif page == "Goals":
    page_goals()
elif page == "Analytics":
    page_analytics()
elif page == "Reports":
    page_reports()
elif page == "Settings":
    page_settings()

# Handle sidebar quick nav intent
if "_nav_to" in st.session_state:
    # simple hint; streamlit reruns will show the selection controls again
    st.sidebar.info(f"Navigate to {st.session_state._nav_to} via the sidebar.")
    del st.session_state["_nav_to"]
