from datetime import datetime
from typing import Literal

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.services.log_parser import build_report_bytes, parse_log_file

router = APIRouter(prefix="/logs", tags=["logs"])

ALLOWED_EXTENSIONS = {".txt", ".log", ".csv"}


@router.post("/api/parse")
async def parse_and_download_report(
    file: UploadFile = File(..., description="Text or CSV log file"),
    format: Literal["csv", "xlsx"] = Query(
        default="csv",
        description="Downloadable report format",
    ),
):
    """Accept a log upload, count error-code frequencies, return a summary file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a .txt, .log, or .csv file.",
        )

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        summary = parse_log_file(file.filename, raw)
        payload, media_type, extension = build_report_bytes(summary, format)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Unable to parse log file: {exc}",
        ) from exc

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    download_name = f"failure_summary_{stamp}.{extension}"
    return Response(
        content=payload,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{download_name}"',
            "X-Total-Error-Codes": str(int(summary["count"].sum()) if not summary.empty else 0),
            "X-Unique-Error-Codes": str(len(summary)),
        },
    )
