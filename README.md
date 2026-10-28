# IT Operations Suite

A portfolio project that packages three practical NOC / IT operations workflows into one FastAPI application:

1. **Incident Tracking** — log, update, and review IT faults across network devices  
2. **Device Monitoring** — background uptime checks for digital-screen endpoints  
3. **Log Parsing & Reporting** — upload text/CSV logs, tally error codes, download a summary report  

Built to demonstrate **backend API design**, **SQLite data modeling**, **async automation**, and **data processing** with a simple Tailwind-powered UI where it helps.

---

## Why this project

IT operations work is rarely one tool. This suite mirrors how a small ops team moves from *ticket → monitor → evidence*:

| Workflow | What it shows |
|----------|----------------|
| Incident Tracking | CRUD APIs, SQLAlchemy models, server-rendered dashboards |
| Device Monitoring | Asyncio background workers, status persistence, failure timestamps |
| Log Parsing | File uploads, pandas aggregation, CSV/Excel report generation |

---

## Features

### 1. IT Incident Tracking
- SQLite model for incidents: `device_id`, `location`, `fault_description`, `status`, `priority`, `resolution_time`
- REST endpoints to create, list, update, and delete incidents
- Tailwind HTML table at `/incidents/` with status and priority highlighting
- Sample incidents seeded on first startup

### 2. Network Device Uptime Monitor
- Async background service that periodically checks a mock list of digital-screen IPs
- Records `online` / `offline` status in the database after each cycle
- Writes a timestamped row to `device_failure_logs` whenever a ping fails
- Configurable check interval and device inventory in `app/config.py`

### 3. Automated Log Parser / Report Generator
- Accepts uploaded `.txt`, `.log`, or `.csv` files
- Uses **pandas** to extract error codes and count failure frequencies
- Returns a downloadable **CSV** or **Excel (`.xlsx`)** summary report
- Sample logs included under `samples/` for quick demos

---

## Tech stack

| Layer | Choice |
|-------|--------|
| API framework | FastAPI |
| Database | SQLite + SQLAlchemy 2.x |
| Validation | Pydantic v2 |
| Background jobs | Python `asyncio` |
| Data / reports | pandas, openpyxl |
| Templates | Jinja2 + Tailwind CSS (CDN) |
| Server | Uvicorn |

---

## Project structure

```text
IT-Operations-Suite/
├── app/
│   ├── main.py                 # FastAPI app + lifespan (DB init, monitor start)
│   ├── config.py               # Settings, mock screen inventory
│   ├── database.py             # SQLite engine & session
│   ├── models/                 # SQLAlchemy models (incidents, devices, failures)
│   ├── schemas/                # Pydantic request/response models
│   ├── routers/                # incidents, uptime, logs
│   ├── services/               # uptime monitor, log parser
│   └── templates/              # Jinja2 + Tailwind pages
├── samples/                    # Demo log files
├── data/                       # SQLite DB (created at runtime, gitignored)
├── static/
├── requirements.txt
└── README.md
```

---

## Getting started

### Prerequisites
- Python 3.11+ recommended
- pip

### Install & run

```bash
git clone https://github.com/<your-username>/IT-Operations-Suite.git
cd IT-Operations-Suite

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- App root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Incidents UI: [http://127.0.0.1:8000/incidents/](http://127.0.0.1:8000/incidents/)

---

## API overview

### Incidents
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/incidents/` | HTML incident table |
| `GET` | `/incidents/api` | List incidents (JSON) |
| `POST` | `/incidents/api` | Create incident |
| `GET` | `/incidents/api/{id}` | Get one incident |
| `PATCH` | `/incidents/api/{id}` | Update incident |
| `DELETE` | `/incidents/api/{id}` | Delete incident |

**Create example**

```bash
curl -X POST http://127.0.0.1:8000/incidents/api \
  -H "Content-Type: application/json" \
  -d "{\"device_id\":\"SW-01\",\"location\":\"Lagos DC\",\"fault_description\":\"Port flapping\",\"status\":\"Open\",\"priority\":\"High\"}"
```

### Uptime monitoring
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/uptime/api/devices` | Current screen online/offline status |
| `GET` | `/uptime/api/failures` | Recent failure log (with timestamps) |

The monitor starts automatically with the app and re-checks devices every **30 seconds** (see `UPTIME_CHECK_INTERVAL_SECONDS`).

### Log parsing
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/logs/api/parse?format=csv` | Upload log → download CSV summary |
| `POST` | `/logs/api/parse?format=xlsx` | Upload log → download Excel summary |

**Parse example**

```bash
curl -F "file=@samples/sample.log" \
  "http://127.0.0.1:8000/logs/api/parse?format=xlsx" \
  -o failure_summary.xlsx
```

Report columns: `error_code`, `count`, `percentage`.

---

## Sample data

| File | Use |
|------|-----|
| `samples/sample.log` | Free-form text log with `error_code=` and `ERR_*` patterns |
| `samples/sample_errors.csv` | Structured CSV with an `error_code` column |

On first launch the app also seeds demo incidents and registers the mock digital-screen inventory from `app/config.py`.

---

## How the automation works

```text
App startup (lifespan)
  ├─ create SQLite tables
  ├─ seed incidents + screen devices
  └─ start asyncio UptimeMonitor loop
        └─ every N seconds:
              mock-ping each screen IP
              update devices.status / last_checked_at
              on failure → set last_failure_at + insert device_failure_logs row
```

Ping checks are **mocked** for a reliable portfolio demo (no ICMP privileges required). Hosts whose last IPv4 octet is listed in `MOCK_OFFLINE_OCTETS` simulate offline screens so failure logging is always visible.

---

## Skills demonstrated

- Designing modular FastAPI routers and shared application lifespan hooks  
- Modeling relational data with SQLAlchemy and serving validated JSON via Pydantic  
- Running non-blocking background monitoring with `asyncio`  
- Parsing operational logs and producing stakeholder-ready reports with pandas  
- Building a lightweight ops UI with Jinja2 templates and Tailwind CSS  

---

## Future improvements

- Persist real ICMP / HTTP health checks behind a feature flag  
- Add authentication and role-based access for ticket updates  
- Live uptime dashboard page (charts for failure frequency over time)  
- Schedule log ingestion from a watched folder or syslog feed  
- Containerize with Docker Compose for one-command demos  

---

## License

MIT — feel free to fork and adapt for your own portfolio or lab environment.
