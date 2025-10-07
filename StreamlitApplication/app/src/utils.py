import streamlit as st

# PUBLIC_INTERFACE
def currency(v: float, symbol: str = "$") -> str:
    """Format a float as currency string."""
    try:
        return f"{symbol}{v:,.2f}"
    except Exception:
        return f"{symbol}0.00"

# PUBLIC_INTERFACE
def validate_positive_number(x, field_name: str):
    """Raise ValueError if number is not positive."""
    if x is None or x < 0:
        raise ValueError(f"{field_name} must be a positive number")

# Static COL index map (simplified demo values)
CITY_COL_INDEX = {
    "New York": 1.25,
    "San Francisco": 1.30,
    "Los Angeles": 1.15,
    "Chicago": 1.05,
    "Austin": 1.00,
    "Remote": 0.95,
}

# PUBLIC_INTERFACE
def col_index_for_city(city: str) -> float:
    """Lookup cost-of-living index for a city; return 1.0 if unknown."""
    if not city:
        return 1.0
    return CITY_COL_INDEX.get(city, 1.0)

# PUBLIC_INTERFACE
def months_of_expense_coverage(ef_amount: float, monthly_expenses: float) -> float:
    """Compute emergency fund coverage in months."""
    if monthly_expenses <= 0:
        return 0.0
    return ef_amount / monthly_expenses

# PUBLIC_INTERFACE
def with_cache_df(key: str, fn):
    """Wrap function with st.cache_data for small dataframes."""
    @st.cache_data(show_spinner=False)
    def _cached():
        return fn()
    return _cached()
