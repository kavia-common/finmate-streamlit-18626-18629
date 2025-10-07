# PUBLIC_INTERFACE
def currency(v: float) -> str:
    """Format a float as currency string."""
    try:
        return f"${v:,.2f}"
    except Exception:
        return "$0.00"

# PUBLIC_INTERFACE
def validate_positive_number(x, field_name: str):
    """Raise ValueError if number is not positive."""
    if x is None or x < 0:
        raise ValueError(f"{field_name} must be a positive number")

# Placeholder for future city COL index integration
CITY_COL_INDEX = {
    # 'San Francisco': 1.3,
}
