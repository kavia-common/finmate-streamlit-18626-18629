from typing import List, Dict

SAFE_SAVINGS_RATE = 0.2  # 20%
DEFAULT_EF_MONTHS = 3
BASELINE_50_30_20 = {"Needs": 0.5, "Wants": 0.3, "Savings/Debt": 0.2}

# PUBLIC_INTERFACE
def default_goals() -> List[str]:
    """Return default financial goals for selection."""
    return [
        "Build Emergency Fund",
        "Pay Off Debt",
        "Invest for Retirement",
        "Save for Big Purchase",
        "Increase Passive Income",
    ]

def compute_budget_breakdown(income: float, expenses: float, col_index: float = 1.0) -> Dict:
    """Compute budget buckets using 50/30/20 baseline adjusted by COL index."""
    actual_savings = max(income - expenses, 0.0)
    base = BASELINE_50_30_20.copy()
    # Adjust needs proportion by COL index (e.g., 1.2 -> 20% more needs share, re-normalize)
    needs = min(base["Needs"] * col_index, 0.85)
    wants = base["Wants"]
    sav = base["Savings/Debt"]
    total = needs + wants + sav
    needs /= total
    wants /= total
    sav /= total
    return {
        "baseline": BASELINE_50_30_20,
        "adjusted": {"Needs": round(needs, 3), "Wants": round(wants, 3), "Savings/Debt": round(sav, 3)},
        "actual_savings": round(actual_savings, 2),
    }

# PUBLIC_INTERFACE
def analyze_finances(
    name: str,
    city: str,
    income: float,
    expenses: float,
    goals: List[str],
    horizon_years: int,
    risk_profile: str = "Balanced",
    emergency_fund_current: float = 0.0,
    emergency_fund_months: int = DEFAULT_EF_MONTHS,
) -> Dict:
    """Analyze user finances and return key metrics, allocations, and recommendations."""
    monthly_savings = max(income - expenses, 0.0)
    savings_rate = 0 if income == 0 else (monthly_savings / income)
    emergency_fund_target = expenses * emergency_fund_months
    ef_gap = max(emergency_fund_target - emergency_fund_current, 0.0)

    # Allocation suggestions
    allocations = {
        "Emergency Fund": 0.0,
        "High-Interest Debt": 0.0,
        "Investments": 0.0,
        "Short-term Savings": 0.0,
        "Discretionary": 0.0,
    }

    remaining = monthly_savings

    if "Build Emergency Fund" in goals and remaining > 0:
        ef_alloc = min(remaining, ef_gap) * 0.5
        allocations["Emergency Fund"] = round(ef_alloc, 2)
        remaining -= ef_alloc

    if "Pay Off Debt" in goals and remaining > 0:
        debt_alloc = remaining * 0.3
        allocations["High-Interest Debt"] = round(debt_alloc, 2)
        remaining -= debt_alloc

    if "Invest for Retirement" in goals and remaining > 0:
        invest_alloc = remaining * (0.6 if risk_profile == "Aggressive" else 0.45 if risk_profile == "Balanced" else 0.3)
        allocations["Investments"] = round(invest_alloc, 2)
        remaining -= invest_alloc

    if "Save for Big Purchase" in goals and remaining > 0:
        st_alloc = remaining * 0.5
        allocations["Short-term Savings"] = round(st_alloc, 2)
        remaining -= st_alloc

    allocations["Discretionary"] = round(max(remaining, 0), 2)

    return {
        "monthly_savings": round(monthly_savings, 2),
        "savings_rate_pct": round(savings_rate * 100, 1),
        "emergency_fund_target": round(emergency_fund_target, 2),
        "emergency_fund_gap": round(ef_gap, 2),
        "investment_budget": round(allocations["Investments"], 2),
        "allocations": allocations,
    }

def retirement_projection(monthly_invest: float, years: int, real_return: float = 0.04):
    """Simple retirement projection with constant real monthly contribution and annual real return."""
    import pandas as pd
    bal = 0.0
    rows = []
    for yr in range(1, years + 1):
        # annualized loop
        for _ in range(12):
            bal = (bal + monthly_invest) * (1 + real_return / 12.0)
        rows.append({"Year": yr, "Balance": round(bal, 2)})
    return pd.DataFrame(rows)

def build_recommendations(analysis: Dict, state) -> List[str]:
    """Create actionable recommendations based on metrics and preferences."""
    recs: List[str] = []
    sr = analysis["savings_rate_pct"] / 100.0
    if sr < SAFE_SAVINGS_RATE:
        target = int(SAFE_SAVINGS_RATE * 100)
        need = analysis["monthly_savings"] * (SAFE_SAVINGS_RATE / max(sr, 0.0001) - 1) if sr > 0 else 0
        recs.append(f"Increase savings to at least {target}%. Consider cutting discretionary spend by ${need:,.0f} or boosting income.")
    else:
        recs.append(f"Your savings rate of {analysis['savings_rate_pct']}% is on track. Maintain momentum.")

    if analysis.get("emergency_fund_gap", 0) > 0:
        recs.append(f"Build emergency fund by ${analysis['emergency_fund_gap']:,.0f} to reach target coverage.")

    inv = analysis["allocations"].get("Investments", 0.0)
    if inv > 0:
        rp = state.user.risk_profile
        if rp == "Aggressive":
            recs.append("Consider 90/10 stock/bond low-cost index allocation.")
        elif rp == "Balanced":
            recs.append("Consider 70/30 diversified index allocation.")
        else:
            recs.append("Consider 50/50 conservative allocation with short-duration bonds.")

    if analysis["allocations"].get("High-Interest Debt", 0) > 0:
        recs.append("Use debt snowball: pay minimums on all debts and direct extra to highest-rate debt first.")

    return recs

def goal_progress_summary(goals: List) -> (str, int):
    """Aggregate progress across goals into a short text and percentage."""
    if not goals:
        return ("No goals set", 0)
    total_target = sum(g.target_amount for g in goals if g.target_amount > 0)
    total_current = sum(min(g.current_amount, g.target_amount) for g in goals)
    if total_target <= 0:
        return ("Targets not specified", 0)
    pct = int(round(100 * total_current / total_target))
    return (f"{pct}% of combined targets saved", pct)
