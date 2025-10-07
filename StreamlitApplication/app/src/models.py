from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

SCHEMA_VERSION = 1


# PUBLIC_INTERFACE
@dataclass
class UserProfile:
    """User profile with core attributes."""
    name: str = ""
    city: str = ""
    age: int = 0
    income: float = 0.0
    risk_profile: str = "Balanced"


@dataclass
class ExpenseItem:
    """Expense item for monthly budget."""
    category: str
    amount: float = 0.0


# PUBLIC_INTERFACE
@dataclass
class Goal:
    """Savings or investment goal with target and current progress."""
    name: str
    target_amount: float
    target_date: str  # ISO date string
    current_amount: float = 0.0

    def dict(self) -> Dict:
        return {
            "name": self.name,
            "target_amount": self.target_amount,
            "target_date": self.target_date,
            "current_amount": self.current_amount,
        }


@dataclass
class Settings:
    """Application settings and preferences."""
    currency_symbol: str = "$"
    emergency_fund_months: int = 3
    emergency_fund_current: float = 0.0
    real_return_assumption: float = 0.04  # annual real return
    retirement_horizon_years: int = 20


# PUBLIC_INTERFACE
@dataclass
class AppState:
    """Top-level persistent application state."""
    version: int
    user: UserProfile
    expenses: List[ExpenseItem]
    goals: List[Goal]
    sessions: Dict[str, Dict]
    settings: Settings

    @staticmethod
    def default() -> "AppState":
        """Create a default initialized state."""
        return AppState(
            version=SCHEMA_VERSION,
            user=UserProfile(),
            expenses=[],
            goals=[],
            sessions={},
            settings=Settings(),
        )

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "user": asdict(self.user),
            "expenses": [asdict(e) for e in self.expenses],
            "goals": [g.dict() for g in self.goals],
            "sessions": self.sessions,
            "settings": asdict(self.settings),
        }

    @staticmethod
    def from_dict(d: Dict) -> "AppState":
        """Construct state from dict (post-migration)."""
        user = d.get("user", {})
        expenses = d.get("expenses", [])
        goals = d.get("goals", [])
        settings = d.get("settings", {})

        return AppState(
            version=d.get("version", SCHEMA_VERSION),
            user=UserProfile(
                name=user.get("name", ""),
                city=user.get("city", ""),
                age=int(user.get("age", 0)),
                income=float(user.get("income", 0.0)),
                risk_profile=user.get("risk_profile", "Balanced"),
            ),
            expenses=[ExpenseItem(category=e.get("category", ""), amount=float(e.get("amount", 0.0))) for e in expenses],
            goals=[Goal(
                name=g.get("name", ""),
                target_amount=float(g.get("target_amount", 0.0)),
                target_date=g.get("target_date", ""),
                current_amount=float(g.get("current_amount", 0.0)),
            ) for g in goals],
            sessions=d.get("sessions", {}),
            settings=Settings(
                currency_symbol=settings.get("currency_symbol", "$"),
                emergency_fund_months=int(settings.get("emergency_fund_months", 3)),
                emergency_fund_current=float(settings.get("emergency_fund_current", 0.0)),
                real_return_assumption=float(settings.get("real_return_assumption", 0.04)),
                retirement_horizon_years=int(settings.get("retirement_horizon_years", 20)),
            ),
        )
