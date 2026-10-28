from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ip_address: str
    status: str
    last_checked_at: datetime | None
    last_failure_at: datetime | None
    created_at: datetime


class DeviceFailureLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    ip_address: str
    failed_at: datetime
    message: str
