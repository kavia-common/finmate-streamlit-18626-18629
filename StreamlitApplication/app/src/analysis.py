from dataclasses import dataclass
from typing import List, Dict

SAFE_SAVINGS_RATE = 0.2  # 20%
EMERGENCY_FUND_MONTHS = 3

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

# PUBLIC_INTERFACE
def analyze_finances(name: str, city: str, income: float, expenses: float, goals: List[str], horizon_years: int) -> Dict:
    """Analyze user finances and return key metrics, allocations, and recommendations."""
    # Basic calculations
    monthly_savings = max(income - expenses, 0)
    savings_rate = 0 if income == 0 else (monthly_savings / income)
    emergency_fund_target = expenses * EMERGENCY_FUND_MONTHS

    # Allocation suggestions based on goals
    allocations = {
        "Emergency Fund": 0.0,
        "High-Interest Debt": 0.0,
        "Investments": 0.0,
        "Short-term Savings": 0.0,
        "Discretionary": 0.0,
    }

    remaining = monthly_savings

    if "Build Emergency Fund" in goals:
        need = max(emergency_fund_target - 0, 0)  # assuming 0 existing for MVP
        ef_alloc = min(remaining, need) * 0.5 if remaining > 0 else 0
        allocations["Emergency Fund"] = round(ef_alloc, 2)
        remaining -= ef_alloc

    if "Pay Off Debt" in goals:
        debt_alloc = remaining * 0.3
        allocations["High-Interest Debt"] = round(debt_alloc, 2)
        remaining -= debt_alloc

    if "Invest for Retirement" in goals:
        invest_alloc = remaining * 0.6
        allocations["Investments"] = round(invest_alloc, 2)
        remaining -= invest_alloc

    if "Save for Big Purchase" in goals:
        st_alloc = remaining * 0.5
        allocations["Short-term Savings"] = round(st_alloc, 2)
        remaining -= st_alloc

    allocations["Discretionary"] = round(max(remaining, 0), 2)

    recommendations = []
    if savings_rate < SAFE_SAVINGS_RATE:
        recommendations.append(
            f"Your savings rate is {round(savings_rate*100,1)}%. Aim for at least {int(SAFE_SAVINGS_RATE*100)}%. Consider reducing discretionary expenses or increasing income."
        )
    else:
        recommendations.append(
            f"Great job! Your savings rate is {round(savings_rate*100,1)}%, which meets or exceeds the target. Maintain this habit."
        )

    if "Investments" in allocations and allocations["Investments"] > 0:
        recommendations.append(
            "Consider a diversified low-cost index fund or a target-date fund suitable for your retirement horizon."
        )
    if "High-Interest Debt" in allocations and allocations["High-Interest Debt"] > 0:
        recommendations.append(
            "Prioritize paying off any high-interest debt (e.g., credit cards) before aggressive investing."
        )

    return {
        "monthly_savings": round(monthly_savings, 2),
        "savings_rate_pct": round(savings_rate * 100, 1),
        "emergency_fund_target": round(emergency_fund_target, 2),
        "investment_budget": round(allocations["Investments"], 2),
        "allocations": allocations,
        "recommendations": recommendations,
    }
