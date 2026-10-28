"""Parse uploaded text/CSV logs and build failure-frequency summaries."""

from __future__ import annotations

import io
import re
from typing import Literal

import pandas as pd

ReportFormat = Literal["csv", "xlsx"]

# Common IT / NOC log patterns that carry an error identifier.
ERROR_CODE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"error[_ ]?code\s*[=:]\s*([A-Za-z0-9_-]+)", re.IGNORECASE),
    re.compile(r"\b(ERR[_-][A-Z0-9_-]+)\b", re.IGNORECASE),
    re.compile(r"\b(E\d{3,5})\b"),
    re.compile(r"\b(CRITICAL|FATAL|FAILURE|ERROR|FAIL)\b", re.IGNORECASE),
]

CSV_ERROR_COLUMNS = {
    "error_code",
    "errorcode",
    "err_code",
    "errcode",
    "code",
    "error",
    "fault_code",
    "faultcode",
}


def _extract_codes_from_text(text: str) -> list[str]:
    codes: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        matched = False
        for pattern in ERROR_CODE_PATTERNS:
            found = pattern.search(line)
            if found:
                codes.append(found.group(1).upper())
                matched = True
                break
        if not matched and re.search(r"\b(error|fail|critical|fatal)\b", line, re.I):
            codes.append("UNSPECIFIED_ERROR")
    return codes


def _extract_codes_from_csv(raw: bytes) -> list[str]:
    df = pd.read_csv(io.BytesIO(raw))
    if df.empty:
        return []

    normalized = {col: re.sub(r"[^a-z0-9]", "", col.lower()) for col in df.columns}
    error_col = next(
        (original for original, key in normalized.items() if key in CSV_ERROR_COLUMNS),
        None,
    )
    if error_col is None:
        # Fall back: scan every cell as free-form log text.
        codes: list[str] = []
        for value in df.astype(str).to_numpy().ravel():
            codes.extend(_extract_codes_from_text(value))
        return codes

    series = df[error_col].dropna().astype(str).str.strip()
    series = series[series != ""]
    return series.str.upper().tolist()


def parse_log_file(filename: str, raw: bytes) -> pd.DataFrame:
    """Return a frequency summary DataFrame: error_code, count, percentage."""
    name = filename.lower()
    if name.endswith(".csv"):
        codes = _extract_codes_from_csv(raw)
    elif name.endswith((".txt", ".log")):
        codes = _extract_codes_from_text(raw.decode("utf-8", errors="replace"))
    else:
        raise ValueError("Unsupported file type. Upload a .txt, .log, or .csv file.")

    if not codes:
        return pd.DataFrame(columns=["error_code", "count", "percentage"])

    summary = (
        pd.Series(codes, name="error_code")
        .value_counts()
        .rename_axis("error_code")
        .reset_index(name="count")
    )
    total = summary["count"].sum()
    summary["percentage"] = (summary["count"] / total * 100).round(2)
    return summary


def build_report_bytes(
    summary: pd.DataFrame,
    fmt: ReportFormat = "csv",
) -> tuple[bytes, str, str]:
    """Serialize summary to CSV or Excel. Returns (payload, media_type, extension)."""
    if fmt == "csv":
        buffer = io.StringIO()
        summary.to_csv(buffer, index=False)
        return buffer.getvalue().encode("utf-8"), "text/csv", "csv"

    if fmt == "xlsx":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            summary.to_excel(writer, index=False, sheet_name="Failure Summary")
        return (
            buffer.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
        )

    raise ValueError("format must be 'csv' or 'xlsx'")
