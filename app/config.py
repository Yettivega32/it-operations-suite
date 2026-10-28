from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'ops_suite.db'}"

# Digital-screen uptime monitor
UPTIME_CHECK_INTERVAL_SECONDS = 30
MOCK_SCREEN_DEVICES = [
    {"name": "Screen — Lagos Lobby", "ip_address": "10.10.1.11"},
    {"name": "Screen — Abuja Gate", "ip_address": "10.10.2.22"},
    {"name": "Screen — Ibadan Concourse", "ip_address": "10.10.3.33"},
    {"name": "Screen — PH Terminal A", "ip_address": "10.10.4.44"},
    {"name": "Screen — Kano Departures", "ip_address": "10.10.5.55"},
]
# Mock IPs whose last octet is divisible by 11 simulate offline (demo failures).
MOCK_OFFLINE_OCTETS = {11, 44}
