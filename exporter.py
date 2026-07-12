"""Orchestrates a Compass query end-to-end: submit, poll, paginate, write to
Excel, and report progress. Used by server.py's export_compass_to_excel tool.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any, Callable

from compass_client import CompassClient, DEFAULT_PAGE_SIZE, get_client
from excel_writer import SplitXlsxWriter

PREVIEW_ROWS = 50


class CompassExporter:
    """One instance per app session. Holds a lazily-created CompassClient and
    tracks the currently running export so it can be cancelled."""

    def __init__(self):
        self._client: CompassClient | None = None
        self._client_lock = threading.Lock()
        self._cancel_event = threading.Event()

    def _get_client(self) -> CompassClient:
        with self._client_lock:
            if self._client is None:
                self._client = get_client()
            return self._client

    def cancel(self):
        self._cancel_event.set()

    def ping(self) -> dict[str, Any]:
        return self._get_client().ping()

    def preview(self, sql: str, limit: int = PREVIEW_ROWS) -> dict[str, Any]:
        """Run the query and return up to `limit` rows for an on-screen preview."""
        client = self._get_client()
        t0 = time.time()
        query_id = client.submit(sql)
        status = client.wait_for_finish(query_id, timeout=180)
        total_rows = status.get("rowCount") or 0
        columns = _columns_from_status(status)

        rows: list[list[Any]] = []
        if total_rows:
            for _, page in client.iter_all_rows(query_id, min(total_rows, limit), page_size=limit):
                if not columns and page and isinstance(page[0], dict):
                    columns = list(page[0].keys())
                rows.extend(_rows_to_values(page, columns))
                break

        return {
            "columns": columns,
            "rows": rows,
            "total_rows": total_rows,
            "elapsed_sec": round(time.time() - t0, 1),
            "query_id": query_id,
        }

    def export(
        self,
        sql: str,
        output_dir: Path,
        base_filename: str,
        rows_per_file: int,
        page_size: int = DEFAULT_PAGE_SIZE,
        on_progress: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        """Run the query in full, streaming results into one or more .xlsx files."""
        self._cancel_event.clear()
        client = self._get_client()

        def report(**kwargs):
            if on_progress:
                on_progress(kwargs)

        t0 = time.time()
        report(phase="submitting")
        query_id = client.submit(sql)

        report(phase="running", query_id=query_id)
        status = client.wait_for_finish(
            query_id, timeout=3600, should_cancel=self._cancel_event.is_set
        )

        total_rows = status.get("rowCount") or 0
        columns = _columns_from_status(status)

        if total_rows == 0:
            report(phase="done", rows_written=0, total_rows=0, files=[])
            return {"row_count": 0, "files": [], "elapsed_sec": round(time.time() - t0, 1)}

        writer: SplitXlsxWriter | None = None
        files: list[Path] = []
        try:
            for offset, page in client.iter_all_rows(
                query_id, total_rows, page_size=page_size, should_cancel=self._cancel_event.is_set
            ):
                if columns is None or not columns:
                    columns = list(page[0].keys()) if page and isinstance(page[0], dict) else []
                if writer is None:
                    writer = SplitXlsxWriter(output_dir / base_filename, columns, rows_per_file)
                values = _rows_to_values(page, columns)
                writer.write_rows(values)
                report(
                    phase="fetching",
                    rows_written=writer.total_rows_written,
                    total_rows=total_rows,
                    elapsed_sec=round(time.time() - t0, 1),
                    files_so_far=len(writer.files_written),
                )
        except InterruptedError:
            if writer is not None:
                files = writer.close()
            report(phase="cancelled", rows_written=writer.total_rows_written if writer else 0, files=[str(f) for f in files])
            return {
                "cancelled": True,
                "row_count": writer.total_rows_written if writer else 0,
                "files": [str(f) for f in files],
                "elapsed_sec": round(time.time() - t0, 1),
            }

        if writer is not None:
            files = writer.close()

        result = {
            "row_count": writer.total_rows_written if writer else 0,
            "files": [str(f) for f in files],
            "elapsed_sec": round(time.time() - t0, 1),
        }
        report(phase="done", **result)
        return result


def _columns_from_status(status: dict[str, Any]) -> list[str]:
    cols_meta = status.get("columns")
    if isinstance(cols_meta, list):
        return [c.get("name", c) if isinstance(c, dict) else c for c in cols_meta]
    return []


def _rows_to_values(page: list[Any], columns: list[str]) -> list[list[Any]]:
    if not page:
        return []
    if isinstance(page[0], dict):
        cols = columns or list(page[0].keys())
        return [[row.get(c) for c in cols] for row in page]
    return page
