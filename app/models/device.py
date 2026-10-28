from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Device(Base):
    """Network endpoint representing a digital screen."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="unknown")
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class DeviceFailureLog(Base):
    """Timestamped record of each offline / ping-failure event."""

    __tablename__ = "device_failure_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id"), nullable=False, index=True
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    failed_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    message: Mapped[str] = mapped_column(Text, nullable=False, default="Ping failed")
