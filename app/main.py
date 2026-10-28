import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, SessionLocal, engine
from app.models.device import Device  # noqa: F401 — register metadata
from app.models.incident import Incident
from app.routers import incidents, logs, uptime
from app.services.uptime import monitor, seed_screen_devices

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def seed_sample_incidents() -> None:
    db = SessionLocal()
    try:
        if db.query(Incident).count() > 0:
            return

        samples = [
            Incident(
                device_id="RTR-CORE-01",
                location="Lagos DC — Rack A12",
                fault_description="BGP session flapping with upstream peer",
                status="Open",
                priority="Critical",
            ),
            Incident(
                device_id="SW-ACCESS-14",
                location="Abuja HQ — Floor 3",
                fault_description="Port 24 down; PoE camera offline",
                status="In Progress",
                priority="High",
            ),
            Incident(
                device_id="FW-EDGE-02",
                location="Ibadan POP",
                fault_description="High CPU during peak traffic window",
                status="Resolved",
                priority="Medium",
                resolution_time=datetime.utcnow() - timedelta(hours=2),
            ),
        ]
        db.add_all(samples)
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_sample_incidents()
    seed_screen_devices()
    monitor.start()
    yield
    await monitor.stop()


app = FastAPI(
    title="IT Operations Suite",
    description="Incident tracking, uptime monitoring, and log reporting",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(incidents.router)
app.include_router(uptime.router)
app.include_router(logs.router)


@app.get("/")
def health():
    return {
        "status": "ok",
        "modules": ["incidents", "uptime", "logs"],
        "incidents_ui": "/incidents/",
        "uptime_devices": "/uptime/api/devices",
        "uptime_failures": "/uptime/api/failures",
        "log_parse": "/logs/api/parse",
    }
