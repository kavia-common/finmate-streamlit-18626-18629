import io
import json
from pathlib import Path
from typing import Dict, Tuple

from .models import AppState, SCHEMA_VERSION

DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
STATE_FILE = DATA_DIR / "state.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def _migrate_state(d: Dict) -> Dict:
    """Migrate older persisted formats to latest schema dict."""
    if not d:
        return AppState.default().to_dict()
    # Detect old sessions-only structure
    if "version" not in d and ("meta" in d or "analysis" in d):
        # Wrap single session payload into sessions dict
        d = {"version": 1, "user": {}, "expenses": [], "goals": [], "sessions": {"imported": d}, "settings": {}}
    if "version" not in d and "sessions" in d and isinstance(d["sessions"], dict):
        d["version"] = 1
    # Ensure required keys
    d.setdefault("user", {})
    d.setdefault("expenses", [])
    d.setdefault("goals", [])
    d.setdefault("sessions", {})
    d.setdefault("settings", {})
    d["version"] = SCHEMA_VERSION
    return d

# PUBLIC_INTERFACE
def load_app_state() -> AppState:
    """Load application state from JSON with migration."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            migrated = _migrate_state(raw)
            return AppState.from_dict(migrated)
        except Exception:
            return AppState.default()
    return AppState.default()

# PUBLIC_INTERFACE
def save_app_state(state: AppState) -> None:
    """Persist application state safely."""
    tmp = STATE_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2)
    tmp.replace(STATE_FILE)

# PUBLIC_INTERFACE
def export_state_json() -> str:
    """Export state to a timestamped file and return path."""
    ts = STATE_FILE.parent / f"state-export-{Path(STATE_FILE).stat().st_mtime_ns}.json"
    with open(ts, "w", encoding="utf-8") as f:
        json.dump(load_app_state().to_dict(), f, indent=2)
    return str(ts)

# PUBLIC_INTERFACE
def import_state_json(uploaded_file) -> Tuple[bool, str]:
    """Import state from an uploaded JSON file-like and persist."""
    try:
        content = uploaded_file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        data = json.loads(content)
        migrated = _migrate_state(data)
        state = AppState.from_dict(migrated)
        save_app_state(state)
        return True, "ok"
    except Exception as e:
        return False, str(e)

# PUBLIC_INTERFACE
def reset_app_state() -> None:
    """Reset state to defaults, keeping directories."""
    state = AppState.default()
    save_app_state(state)

# Legacy compatibility helpers
# PUBLIC_INTERFACE
def load_sessions() -> Dict:
    """Legacy: return sessions mapping from current state."""
    return load_app_state().sessions

# PUBLIC_INTERFACE
def save_session(name: str, payload: Dict) -> None:
    """Legacy: save a single session into state.sessions."""
    s = load_app_state()
    s.sessions[name] = payload
    save_app_state(s)
