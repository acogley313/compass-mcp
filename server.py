#!/usr/bin/env python3
"""
Compass MCP Server
==================
A thin MCP server that wraps the Infor Compass (Data Fabric) SQL API so Claude
can run SQL queries against Infor directly from chat.

Credentials are read from standard Infor `.ionapi` files (the native format you
download from the ION API portal). Nothing is hardcoded. To move this to another
machine, copy the whole folder — that's it.

Two environments are supported: production and training (TRN).

Tools exposed:
  Production (credentials.ionapi / IONAPI_FILE):
    - query_compass(sql):              submit SQL, poll until done, return rows + columns
    - ping_compass():                  check Compass connectivity
    - export_compass_to_excel(sql):    export full result set to Excel
    - fetch_csd(table, where):         read live CSD directly (bypasses the Compass replica)
    - export_csd_to_excel(table, where): export a full live CSD table/filter to Excel

  Training (credentials_trn.ionapi / IONAPI_FILE_TRN):
    - query_compass_trn(sql):          same as query_compass but against TRN
    - ping_compass_trn():              check TRN Compass connectivity
    - export_compass_to_excel_trn(sql): same as export_compass_to_excel but against TRN
    - fetch_csd_trn(table, where):     same as fetch_csd but against TRN
    - export_csd_to_excel_trn(table, where): same as export_csd_to_excel but against TRN

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

from compass_client import CompassClient, get_client, get_client_for_env
from exporter import CompassExporter
from exporter import export_csd_to_excel as _write_csd_excel

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

_compass_prod: CompassClient | None = None
_compass_trn: CompassClient | None = None
_exporter_prod: CompassExporter | None = None
_exporter_trn: CompassExporter | None = None


def _get_client_prod() -> CompassClient:
    global _compass_prod
    if _compass_prod is None:
        _compass_prod = get_client_for_env(
            env_var="IONAPI_FILE",
            default_name="credentials.ionapi",
            base_url_env="COMPASS_BASE_URL",
            csd_base_url_env="CSD_BASE_URL",
        )
    return _compass_prod


def _get_client_trn() -> CompassClient:
    global _compass_trn
    if _compass_trn is None:
        _compass_trn = get_client_for_env(
            env_var="IONAPI_FILE_TRN",
            default_name="credentials_trn.ionapi",
            base_url_env="COMPASS_BASE_URL_TRN",
            csd_base_url_env="CSD_BASE_URL_TRN",
        )
    return _compass_trn


def _csd_config(trn: bool) -> tuple[str, int] | dict[str, Any]:
    """(operator, company_number) for FetchWhere, or an error dict if unset.

    The operator init is per-person and has no default. TRN looks for
    CSD_OPERATOR_INIT_TRN / CSD_COMPANY_NUMBER_TRN first and falls back to the
    shared CSD_OPERATOR_INIT / CSD_COMPANY_NUMBER (company defaults to 1).
    """
    suffix = "_TRN" if trn else ""
    operator = os.environ.get(f"CSD_OPERATOR_INIT{suffix}") or os.environ.get("CSD_OPERATOR_INIT")
    if not operator:
        return {
            "error": "config_missing",
            "message": (
                'CSD_OPERATOR_INIT is not set. Add it to this server\'s "env" '
                "block in claude_desktop_config.json (your CSD operator/login "
                'code, e.g. "AC01") and restart Claude Desktop.'
                + (" For TRN you can set CSD_OPERATOR_INIT_TRN if your training code differs." if trn else "")
            ),
        }
    company = int(os.environ.get(f"CSD_COMPANY_NUMBER{suffix}") or os.environ.get("CSD_COMPANY_NUMBER") or "1")
    return operator, company


def _fetch_csd(trn: bool, table: str, where: str, max_rows: int) -> dict[str, Any]:
    """Shared body of fetch_csd / fetch_csd_trn."""
    cfg = _csd_config(trn)
    if isinstance(cfg, dict):
        return cfg
    operator, company = cfg
    try:
        client = _get_client_trn() if trn else _get_client_prod()
        all_rows: list[dict[str, Any]] = []
        truncated = False
        for batch in client.iter_csd_fetch_where(
            table=table,
            where_clause=where,
            operator=operator,
            company_number=company,
        ):
            all_rows.extend(batch)
            if len(all_rows) >= max_rows:
                truncated = True
                all_rows = all_rows[:max_rows]
                break
        columns = list(all_rows[0].keys()) if all_rows else []
        rows = [[row.get(c) for c in columns] for row in all_rows]
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": truncated,
        }
    except Exception as e:
        return {"error": "fetch_failed", "message": str(e)}


def _export_csd(
    trn: bool, table: str, where: str, filename: str, rows_per_file: int
) -> dict[str, Any]:
    """Shared body of export_csd_to_excel / export_csd_to_excel_trn."""
    cfg = _csd_config(trn)
    if isinstance(cfg, dict):
        return cfg
    operator, company = cfg
    try:
        client = _get_client_trn() if trn else _get_client_prod()
        return _write_csd_excel(
            client,
            table,
            where,
            operator,
            company,
            output_dir=Path.home() / "Downloads",
            base_filename=filename or f"csd_{table.lower()}",
            rows_per_file=max(1000, int(rows_per_file or 100_000)),
        )
    except Exception as e:
        return {"error": "export_failed", "message": str(e)}


def _get_exporter_prod() -> CompassExporter:
    global _exporter_prod
    if _exporter_prod is None:
        _exporter_prod = CompassExporter(
            env_var="IONAPI_FILE",
            default_name="credentials.ionapi",
            base_url_env="COMPASS_BASE_URL",
        )
    return _exporter_prod


def _get_exporter_trn() -> CompassExporter:
    global _exporter_trn
    if _exporter_trn is None:
        _exporter_trn = CompassExporter(
            env_var="IONAPI_FILE_TRN",
            default_name="credentials_trn.ionapi",
            base_url_env="COMPASS_BASE_URL_TRN",
        )
    return _exporter_trn


@mcp.tool()
def query_compass(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    """Run a SQL query against the production Infor Compass environment and return the results.

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
        client = _get_client_prod()
        raw = client.run_query(sql, max_rows)
        result = normalize_result(raw, max_rows)
        result["query_id"] = raw.get("query_id")
        return result
    except TimeoutError as e:
        return {"error": "timeout", "message": str(e)}
    except Exception as e:
        return {"error": "query_failed", "message": str(e)}


@mcp.tool()
def fetch_csd(table: str, where: str = "", max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    """Read rows straight from the live PRODUCTION CSD/SX.e database, bypassing
    the Compass datalake replica that `query_compass` uses.

    Use this instead of `query_compass` when the datalake copy might be out
    of sync with CSD (e.g. a record was just changed and hasn't shown up in
    Compass yet), or when the user explicitly asks for "live"/"current"/
    "right now" data. Trade-offs versus `query_compass`:
      - No SQL, no joins, no picking columns: give a table name and an
        optional WHERE clause, and every column on that table comes back.
      - Much faster for a single table, and paginates cleanly.
      - String literals in the WHERE clause must be double-quoted, e.g.
        `whse = "TN01"` — single quotes are rejected.

    Args:
        table: CSD table name (e.g. "icsw", "arsc", "pdsc"). Case-insensitive.
        where: Optional WHERE clause with no "WHERE" keyword, e.g.
            'cono = 1 and whse = "TN01"'. Leave blank to return every row.
        max_rows: Maximum number of rows to return (default 1000). Pages are
            fetched from CSD until this many rows are collected or the table
            is exhausted.

    If the response comes back with `truncated: true`, or the user wants a whole
    table, use `export_csd_to_excel` instead of raising max_rows.

    Returns:
        A dict with `columns` (list of column names) and `rows` (list of row
        value lists), plus `row_count` and `truncated`. On failure, returns a
        dict with an `error` message.
    """
    return _fetch_csd(False, table, where, max_rows)


@mcp.tool()
def export_csd_to_excel(
    table: str,
    where: str = "",
    filename: str = "",
    rows_per_file: int = 100_000,
) -> dict[str, Any]:
    """Export a full table (or WHERE-filtered slice) of the live PRODUCTION CSD/SX.e
    database to one or more .xlsx files in the user's Downloads folder,
    instead of returning rows in chat.

    This is the Excel export for `fetch_csd`: use it instead of `fetch_csd` when the
    result is too big for chat — after `fetch_csd` reports `truncated: true`, or up
    front when the user wants a whole table (e.g. "all ICSW items") or any
    large pull. Like `fetch_csd` it reads CSD directly (no datalake replica),
    takes a table name plus an optional WHERE clause (double-quoted string
    literals, e.g. `whse = "TN01"`), and always writes EVERY column of the
    table — no SQL, joins, or column selection. Rows stream to disk page by
    page, so very large tables are fine, but they take time (roughly 900
    rows/s on a wide table like ICSW; a few hundred thousand rows is several
    minutes) — that's expected, not a hang. If a pull is huge, filter it with
    `where` (e.g. one warehouse or vendor at a time) and export in pieces.
    Files auto-split every `rows_per_file` rows.

    Args:
        table: CSD table name (e.g. "icsw", "arsc", "pdsc"). Case-insensitive.
        where: Optional WHERE clause with no "WHERE" keyword, e.g.
            'cono = 1 and statustype <> "I"'. Leave blank for every row.
        filename: Base file name, no extension (default "csd_<table>"). Saved
            as `<filename>.xlsx`, or `<filename>_part1.xlsx`,
            `<filename>_part2.xlsx`, ... if the result spans several files.
        rows_per_file: Max data rows per file (default 100,000 — lower than
            the Compass export because every column comes back, so files
            get wide).

    Returns:
        A dict with `files` (absolute paths written to Downloads),
        `row_count`, `column_count` and `elapsed_sec`. On failure, returns a
        dict with an `error` message; anything already written is kept.
    """
    return _export_csd(False, table, where, filename, rows_per_file)


@mcp.tool()
def export_compass_to_excel(
    sql: str,
    filename: str = "compass_export",
    rows_per_file: int = 500_000,
) -> dict[str, Any]:
    """Run a SQL query against the production Infor Compass environment and stream the *entire* result
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
        exporter = _get_exporter_prod()
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
    """Check connectivity to the production Infor Compass API.

    Returns a dict indicating whether Compass is reachable and authenticated.
    """
    try:
        client = _get_client_prod()
        return client.ping()
    except Exception as e:
        return {"ok": False, "error": "ping_failed", "message": str(e)}


# ---- Training (TRN) environment tools ----------------------------------------

@mcp.tool()
def query_compass_trn(sql: str, max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    """Run a SQL query against the training (TRN) Infor Compass environment and return the results.

    If the response comes back with `truncated: true`, the query has more
    rows than fit here — re-run the same SQL through
    `export_compass_to_excel_trn` instead of raising max_rows, so the full result
    set gets written to an Excel file in Downloads rather than dumped into
    chat. Also prefer `export_compass_to_excel_trn` up front, without probing
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
        client = _get_client_trn()
        raw = client.run_query(sql, max_rows)
        result = normalize_result(raw, max_rows)
        result["query_id"] = raw.get("query_id")
        return result
    except TimeoutError as e:
        return {"error": "timeout", "message": str(e)}
    except Exception as e:
        return {"error": "query_failed", "message": str(e)}


@mcp.tool()
def export_compass_to_excel_trn(
    sql: str,
    filename: str = "compass_export",
    rows_per_file: int = 500_000,
) -> dict[str, Any]:
    """Run a SQL query against the training (TRN) Infor Compass environment and stream the *entire* result
    set into one or more .xlsx files in the user's Downloads folder, instead
    of returning rows in chat.

    Use this — instead of `query_compass_trn` — whenever a result set is too big
    for chat: after `query_compass_trn` reports `truncated: true`, or up front
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
        exporter = _get_exporter_trn()
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
def ping_compass_trn() -> dict[str, Any]:
    """Check connectivity to the training (TRN) Infor Compass API.

    Returns a dict indicating whether TRN Compass is reachable and authenticated.
    """
    try:
        client = _get_client_trn()
        return client.ping()
    except Exception as e:
        return {"ok": False, "error": "ping_failed", "message": str(e)}


@mcp.tool()
def fetch_csd_trn(table: str, where: str = "", max_rows: int = DEFAULT_MAX_ROWS) -> dict[str, Any]:
    """Read rows straight from the live TRAINING (TRN) CSD/SX.e database,
    bypassing the Compass datalake replica that `query_compass_trn` uses.

    Same behavior as `fetch_csd`, but against the training environment: no
    SQL, no joins, no picking columns (every column on the table comes back),
    fast and paginated, and string literals in the WHERE clause must be
    double-quoted, e.g. `whse = "TN01"`. Use it when the TRN datalake copy
    might be stale or the user asks for live training data.

    Args:
        table: CSD table name (e.g. "icsw", "arsc", "pdsc"). Case-insensitive.
        where: Optional WHERE clause with no "WHERE" keyword, e.g.
            'cono = 1 and whse = "TN01"'. Leave blank to return every row.
        max_rows: Maximum number of rows to return (default 1000).

    If the response comes back with `truncated: true`, or the user wants a whole
    table, use `export_csd_to_excel_trn` instead of raising max_rows.

    Returns:
        A dict with `columns`, `rows`, `row_count` and `truncated`. On
        failure, returns a dict with an `error` message.
    """
    return _fetch_csd(True, table, where, max_rows)


@mcp.tool()
def export_csd_to_excel_trn(
    table: str,
    where: str = "",
    filename: str = "",
    rows_per_file: int = 100_000,
) -> dict[str, Any]:
    """Export a full table (or WHERE-filtered slice) of the live TRAINING (TRN) CSD/SX.e
    database to one or more .xlsx files in the user's Downloads folder,
    instead of returning rows in chat.

    This is the Excel export for `fetch_csd_trn`: use it instead of `fetch_csd_trn` when the
    result is too big for chat — after `fetch_csd_trn` reports `truncated: true`, or up
    front when the user wants a whole table (e.g. "all ICSW items") or any
    large pull. Like `fetch_csd_trn` it reads CSD directly (no datalake replica),
    takes a table name plus an optional WHERE clause (double-quoted string
    literals, e.g. `whse = "TN01"`), and always writes EVERY column of the
    table — no SQL, joins, or column selection. Rows stream to disk page by
    page, so very large tables are fine, but they take time (roughly 900
    rows/s on a wide table like ICSW; a few hundred thousand rows is several
    minutes) — that's expected, not a hang. If a pull is huge, filter it with
    `where` (e.g. one warehouse or vendor at a time) and export in pieces.
    Files auto-split every `rows_per_file` rows.

    Args:
        table: CSD table name (e.g. "icsw", "arsc", "pdsc"). Case-insensitive.
        where: Optional WHERE clause with no "WHERE" keyword, e.g.
            'cono = 1 and statustype <> "I"'. Leave blank for every row.
        filename: Base file name, no extension (default "csd_<table>"). Saved
            as `<filename>.xlsx`, or `<filename>_part1.xlsx`,
            `<filename>_part2.xlsx`, ... if the result spans several files.
        rows_per_file: Max data rows per file (default 100,000 — lower than
            the Compass export because every column comes back, so files
            get wide).

    Returns:
        A dict with `files` (absolute paths written to Downloads),
        `row_count`, `column_count` and `elapsed_sec`. On failure, returns a
        dict with an `error` message; anything already written is kept.
    """
    return _export_csd(True, table, where, filename, rows_per_file)


if __name__ == "__main__":
    # Quick CLI self-test:  python server.py --selftest [--trn]
    if "--selftest" in sys.argv:
        test_trn = "--trn" in sys.argv
        label = "TRN" if test_trn else "Production"
        print(f"Loading {label} credentials...", file=sys.stderr)
        c = _get_client_trn() if test_trn else _get_client_prod()
        print(f"Token URL:    {c.cfg.token_url}", file=sys.stderr)
        print(f"Grant type:   {c.cfg.grant_type}", file=sys.stderr)
        print(f"Scope:        {' '.join(c.cfg.scopes) or '(none sent)'}", file=sys.stderr)
        if c.cfg.grant_type == "password":
            print("Note:         password grant in use; client_credentials is recommended "
                  "(see README: 'OAuth grant types and scopes').", file=sys.stderr)
        print(f"Compass base: {c.cfg.compass_base}", file=sys.stderr)
        print(f"Pinging {label} Compass...", file=sys.stderr)
        print(json.dumps(c.ping(), indent=2), file=sys.stderr)
        sys.exit(0)

    mcp.run()
