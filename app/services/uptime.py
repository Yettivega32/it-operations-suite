"""Background uptime monitor for mock digital-screen IP addresses.

Uses asyncio so it fits cleanly into FastAPI's lifespan without blocking
request handlers. Ping checks are mocked (deterministic online/offline) so
the demo works without real ICMP privileges or reachable LAN hosts.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from app.config import (
    MOCK_OFFLINE_OCTETS,
    MOCK_SCREEN_DEVICES,
    UPTIME_CHECK_INTERVAL_SECONDS,
)
from app.database import SessionLocal
from app.models.device import Device, DeviceFailureLog

logger = logging.getLogger("uptime.monitor")


async def mock_ping(ip_address: str) -> bool:
    """Simulate a network ping with a short async delay.

    Returns True when the host is considered online. Hosts whose last IPv4
    octet is listed in MOCK_OFFLINE_OCTETS are treated as unreachable so the
    failure path (DB status + failure log) can be demonstrated.
    """
    await asyncio.sleep(0.05)
    try:
        last_octet = int(ip_address.rsplit(".", 1)[-1])
    except ValueError:
        return False
    return last_octet not in MOCK_OFFLINE_OCTETS


def seed_screen_devices() -> None:
    db = SessionLocal()
    try:
        for entry in MOCK_SCREEN_DEVICES:
            existing = (
                db.query(Device)
                .filter(Device.ip_address == entry["ip_address"])
                .one_or_none()
            )
            if existing is None:
                db.add(
                    Device(
                        name=entry["name"],
                        ip_address=entry["ip_address"],
                        status="unknown",
                    )
                )
        db.commit()
    finally:
        db.close()


def _record_check_results(results: list[tuple[int, str, bool]]) -> None:
    """Persist online/offline status; append a failure log row on each miss."""
    checked_at = datetime.utcnow()
    db = SessionLocal()
    try:
        for device_id, ip_address, is_online in results:
            device = db.get(Device, device_id)
            if device is None:
                continue

            device.last_checked_at = checked_at
            if is_online:
                device.status = "online"
                logger.info("Screen online: %s (%s)", device.name, ip_address)
            else:
                device.status = "offline"
                device.last_failure_at = checked_at
                db.add(
                    DeviceFailureLog(
                        device_id=device.id,
                        ip_address=ip_address,
                        failed_at=checked_at,
                        message=f"Ping failed for {ip_address}",
                    )
                )
                logger.warning(
                    "Screen OFFLINE: %s (%s) at %s",
                    device.name,
                    ip_address,
                    checked_at.isoformat(timespec="seconds"),
                )
        db.commit()
    finally:
        db.close()


async def run_check_cycle() -> None:
    db = SessionLocal()
    try:
        devices = db.query(Device).order_by(Device.id).all()
        targets = [(d.id, d.ip_address) for d in devices]
    finally:
        db.close()

    if not targets:
        logger.debug("No devices to monitor")
        return

    ping_tasks = [mock_ping(ip) for _, ip in targets]
    online_flags = await asyncio.gather(*ping_tasks)
    results = [
        (device_id, ip, is_online)
        for (device_id, ip), is_online in zip(targets, online_flags)
    ]
    await asyncio.to_thread(_record_check_results, results)


class UptimeMonitor:
    """Async background loop that periodically checks screen reachability."""

    def __init__(self, interval_seconds: int = UPTIME_CHECK_INTERVAL_SECONDS):
        self.interval_seconds = interval_seconds
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def _loop(self) -> None:
        logger.info(
            "Uptime monitor started (interval=%ss, devices=%s)",
            self.interval_seconds,
            len(MOCK_SCREEN_DEVICES),
        )
        while not self._stop.is_set():
            try:
                await run_check_cycle()
            except Exception:
                logger.exception("Uptime check cycle failed")
            try:
                await asyncio.wait_for(
                    self._stop.wait(), timeout=self.interval_seconds
                )
            except asyncio.TimeoutError:
                continue
        logger.info("Uptime monitor stopped")

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._stop.clear()
            self._task = asyncio.create_task(self._loop(), name="uptime-monitor")

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            await self._task
            self._task = None


monitor = UptimeMonitor()
