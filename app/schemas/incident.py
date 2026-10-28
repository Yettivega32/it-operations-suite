from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=200)
    fault_description: str = Field(..., min_length=1)
    status: str = Field(default="Open", max_length=50)
    priority: str = Field(default="Medium", max_length=20)
    resolution_time: datetime | None = None


class IncidentUpdate(BaseModel):
    device_id: str | None = Field(default=None, min_length=1, max_length=100)
    location: str | None = Field(default=None, min_length=1, max_length=200)
    fault_description: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, max_length=50)
    priority: str | None = Field(default=None, max_length=20)
    resolution_time: datetime | None = None


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    location: str
    fault_description: str
    status: str
    priority: str
    resolution_time: datetime | None
    created_at: datetime
