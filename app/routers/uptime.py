from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.device import Device, DeviceFailureLog
from app.schemas.device import DeviceFailureLogRead, DeviceRead

router = APIRouter(prefix="/uptime", tags=["uptime"])


@router.get("/api/devices", response_model=list[DeviceRead])
def list_devices(db: Session = Depends(get_db)):
    return db.query(Device).order_by(Device.name).all()


@router.get("/api/failures", response_model=list[DeviceFailureLogRead])
def list_failures(limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(DeviceFailureLog)
        .order_by(DeviceFailureLog.failed_at.desc())
        .limit(min(limit, 200))
        .all()
    )
