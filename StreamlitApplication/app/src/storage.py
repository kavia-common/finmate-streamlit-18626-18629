import json
from pathlib import Path
from typing import Dict

DATA_DIR = Path("data")
SESSIONS_FILE = DATA_DIR / "sessions.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# PUBLIC_INTERFACE
def load_sessions() -> Dict:
    """Load saved sessions from local JSON file."""
    if SESSIONS_FILE.exists():
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

# PUBLIC_INTERFACE
def save_session(name: str, payload: Dict) -> None:
    """Persist a single session payload into the sessions JSON."""
    sessions = load_sessions()
    sessions[name] = payload
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)
