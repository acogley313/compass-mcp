#!/usr/bin/env python3
"""
Compass MCP Server
==================
A thin MCP server that wraps the Infor Compass (Data Fabric) SQL API so Claude
can run SQL queries against Infor directly from chat.

Credentials are read from a standard Infor `.ionapi` file (the native format you
download from the ION API portal). Nothing is hardcoded. To move this to another
machine, copy the whole folder — that's it.

Tools exposed:
  - query_compass(sql): submit SQL, poll until done, return rows + columns
  - ping_compass():     check Compass connectivity

The actual HTTP/auth logic lives in compass_client.py, shared with the desktop
query app in app/.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from compass_client import CompassClient, get_client
from exporter import CompassExporter

# Default row cap so responses stay manageable. Override with COMPASS_MAX_ROWS.
DEFAULT_MAX_ROWS = int(os.environ.get("COMPASS_MAX_ROWS", "1000"))


# --------------------------------------------------------------------------- #
# Normalize results into rows + columns
# --------------------------------------------------------------------------- #

def normalize_result(res: dict[str, Any], max_rows: int) -> dict[str, Any]:
    """Best-effort flatten of the Compass result into {columns, rows, row_count}."""
    if res.get("format") == "text":
        return {"columns": [], "rows": [], "raw_text": res["data"][:50000]}

    data = res["data"]

    columns: list[str] = []
    rows: list[Any] = []

    if isinstance(data, dict):
        if "columns" in data and "rows" in data:
            cols = data["columns"]
            columns = [c.get("name", c) if isinstance(c, dict) else c for c in cols]
            rows = data["rows"]
        else:
            records = (
                data.get("results")
                or data.get("data")
                or data.get("records")
                or data.get("items")
            )
            if isinstance(records, list):
                rows, columns = _records_to_rows(records)
            else:
                return {"columns": [], "rows": [], "raw": data}
    elif isinstance(data, list):
        rows, columns = _records_to_rows(data)
    else:
        return {"columns": [], "rows": [], "raw": data}

    if not columns and res.get("status_columns"):
        columns = res["status_columns"]

    truncated = len(rows) > max_rows
    rows = rows[:max_rows]
    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "truncated": truncated,
    }


def _records_to_rows(records: list[Any]) -> tuple[list[Any], list[str]]:
    if records and isinstance(records[0], dict):
        columns = list(records[0].keys())
        rows = [[rec.get(c) for c in columns] for rec in records]
        return rows, columns
    return records, []


# --------------------------------------------------------------------------- #
# MCP server wiring
# --------------------------------------------------------------------------- #

mcp = FastMCP("compass")

_compass: CompassClient | None = None
_exporter: CompassExporter | None = None


def _get_client() -> CompassClient:
    global _compass
    if _compass is None:
        _compass = get_client()
    return _compass


def _get_exporter() -> CompassExporter:
    global _exporter
    if _exporter is None:
        _exporter = CompassExporter()
    return _exporter


@mcp.tool()
def query_compass(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    """Run a SQL query against Infor Compass and return the results.

    If the response comes back with `truncated: true`, the query has more
    rows than fit here — re-run the same SQL through
    `export_compass_to_excel` instead of raising max_rows, so the full result
    set gets written to an Excel file in Downloads rather than dumped into
    chat. Also prefer `export_compass_to_excel` up front, without probing
    with this tool first, whenever the user's request implies a large or
    complete result set (e.g. "export", "full table", "all records",
    "every transaction", or anything you'd expect to run into the tens of
    thousands of rows or more).

    Args:
        sql: The SQL statement to execute (Compass SQL dialect).
        max_rows: Maximum number of rows to return (default 1000).

    Returns:
        A dict with `columns` (list of column names) and `rows` (list of row
        value lists), plus `row_count` and `truncated`. On failure, returns a
        dict with an `error` message.
    """
    try:
        client = _get_client()
        raw = client.run_query(sql, max_rows)
        result = normalize_result(raw, max_rows)
        result["query_id"] = raw.get("query_id")
        return result
    except TimeoutError as e:
        return {"error": "timeout", "message": str(e)}
    except Exception as e:
        return {"error": "query_failed", "message": str(e)}


@mcp.tool()
def export_compass_to_excel(
    sql: str,
    filename: str = "compass_export",
    rows_per_file: int = 500_000,
) -> dict[str, Any]:
    """Run a SQL query against Infor Compass and stream the *entire* result
    set into one or more .xlsx files in the user's Downloads folder, instead
    of returning rows in chat.

    Use this — instead of `query_compass` — whenever a result set is too big
    for chat: after `query_compass` reports `truncated: true`, or up front
    when the user's request implies a full/large export. There's no row cap
    here; results are paged from Compass and written straight to disk (never
    held fully in memory), so this comfortably handles result sets up to
    Compass's practical limit (roughly 1.5M rows). Files auto-split every
    `rows_per_file` rows to stay under Excel's 1,048,576-row-per-sheet limit.
    Large exports can take a few minutes — that's expected, not a hang.

    Args:
        sql: The SQL statement to execute (Compass SQL dialect).
        filename: Base file name, no extension (default "compass_export").
            Saved as `<filename>.xlsx`, or `<filename>_part1.xlsx`,
            `<filename>_part2.xlsx`, ... if the result spans multiple files.
        rows_per_file: Max data rows per file (default 500,000; always
            clamped under Excel's hard per-sheet limit).

    Returns:
        A dict with `files` (absolute paths written to Downloads),
        `row_count`, and `elapsed_sec`. On failure, returns a dict with an
        `error` message; anything already written to disk is kept.
    """
    try:
        exporter = _get_exporter()
        result = exporter.export(
            sql,
            output_dir=Path.home() / "Downloads",
            base_filename=filename or "compass_export",
            rows_per_file=max(1000, int(rows_per_file or 500_000)),
        )
        return result
    except TimeoutError as e:
        return {"error": "timeout", "message": str(e)}
    except Exception as e:
        return {"error": "export_failed", "message": str(e)}


@mcp.tool()
def ping_compass() -> dict[str, Any]:
    """Check connectivity to the Infor Compass API.

    Returns a dict indicating whether Compass is reachable and authenticated.
    """
    try:
        client = _get_client()
        return client.ping()
    except Exception as e:
        return {"ok": False, "error": "ping_failed", "message": str(e)}


if __name__ == "__main__":
    # Quick CLI self-test:  python server.py --selftest
    if "--selftest" in sys.argv:
        print("Loading credentials...", file=sys.stderr)
        c = _get_client()
        print(f"Token URL:    {c.cfg.token_url}", file=sys.stderr)
        print(f"Compass base: {c.cfg.compass_base}", file=sys.stderr)
        print("Pinging Compass...", file=sys.stderr)
        print(json.dumps(c.ping(), indent=2), file=sys.stderr)
        sys.exit(0)

    mcp.run()
