"""Streaming, auto-splitting XLSX writer.

Writes rows to disk as they arrive (xlsxwriter constant_memory mode) so
exports of hundreds of thousands to millions of rows don't blow up memory.
Automatically starts a new file/part when a row limit is hit, since Excel
sheets cap out at 1,048,576 rows and huge single files are unwieldy anyway.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import xlsxwriter

# Excel's hard per-sheet row cap (including the header row).
EXCEL_MAX_ROWS = 1_048_576


class SplitXlsxWriter:
    def __init__(self, base_path: Path, columns: list[str], rows_per_file: int):
        """
        base_path: full path *without* extension, e.g. .../Downloads/my_query
        columns: header row, fixed for the life of this writer
        rows_per_file: max data rows per file part (auto-clamped under Excel's cap)
        """
        self.base_path = base_path
        self.columns = columns
        self.rows_per_file = min(rows_per_file, EXCEL_MAX_ROWS - 1)

        self._part = 0
        self._workbook = None
        self._sheet = None
        self._row_in_file = 0
        self.total_rows_written = 0
        self.files_written: list[Path] = []

        self._open_new_file()

    def _open_new_file(self):
        if self._workbook is not None:
            self._close_current()
        self._part += 1
        path = self.base_path.parent / f"{self.base_path.name}_part{self._part}.xlsx"
        self.files_written.append(path)
        self._workbook = xlsxwriter.Workbook(str(path), {"constant_memory": True})
        self._sheet = self._workbook.add_worksheet("data")
        for col_idx, name in enumerate(self.columns):
            self._sheet.write(0, col_idx, str(name))
        self._row_in_file = 1  # next write goes to row index 1 (row 0 is header)

    def _close_current(self):
        self._workbook.close()

    def write_rows(self, rows: list[list[Any]]):
        for row in rows:
            if self._row_in_file - 1 >= self.rows_per_file:
                self._open_new_file()
            for col_idx, value in enumerate(row):
                self._sheet.write(self._row_in_file, col_idx, _coerce(value))
            self._row_in_file += 1
            self.total_rows_written += 1

    def close(self) -> list[Path]:
        self._close_current()
        # If everything fit in one file, drop the "_part1" suffix for a clean name.
        if len(self.files_written) == 1:
            clean = self.base_path.with_suffix(".xlsx")
            only = self.files_written[0]
            if only != clean:
                if clean.exists():
                    clean.unlink()
                only.rename(clean)
                self.files_written[0] = clean
        return self.files_written


def _coerce(value: Any) -> Any:
    """xlsxwriter chokes on non-primitive types, NaN/Inf, and overlong strings; sanitize those."""
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
            return str(value)
        return value
    if not isinstance(value, str):
        value = str(value)
    return value[:32767] if len(value) > 32767 else value
