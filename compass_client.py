#!/usr/bin/env python3
"""
Compass API client
===================
Shared connection layer for talking to Infor Compass (Data Fabric). Used by
both the MCP server (server.py) and the desktop query app (app/).

Handles ION API OAuth2 auth, submitting SQL jobs, polling for completion, and
paginating through results.
"""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

import httpx

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

POLL_TIMEOUT = int(os.environ.get("COMPASS_POLL_TIMEOUT", "120"))
POLL_INTERVAL = float(os.environ.get("COMPASS_POLL_INTERVAL", "2"))
HTTP_TIMEOUT = float(os.environ.get("COMPASS_HTTP_TIMEOUT", "60"))

# Compass caps a single result page at ~10MB. Start requests at this many rows
# and halve on a "page too large" error until one fits, then reuse that size.
DEFAULT_PAGE_SIZE = int(os.environ.get("COMPASS_PAGE_SIZE", "25000"))
MIN_PAGE_SIZE = 200

PAGE_TOO_LARGE_CODE = "760"


def find_ionapi_file(start: Path | None = None) -> Path:
    """Locate the .ionapi credentials file.

    Priority:
      1. IONAPI_FILE env var (absolute or relative path)
      2. credentials.ionapi next to this module
      3. the first *.ionapi file next to this module
      4. ~/compass-mcp/credentials.ionapi — the standard install location used
         by install.command/install.bat, so standalone tools (like the Query
         App shared on its own) can find credentials from an existing
         compass-mcp install without needing their own copy.
    """
    env_path = os.environ.get("IONAPI_FILE")
    if env_path:
        p = Path(env_path).expanduser()
        if not p.is_file():
            raise FileNotFoundError(f"IONAPI_FILE points to a missing file: {p}")
        return p

    here = (start or Path(__file__).resolve().parent)
    default = here / "credentials.ionapi"
    if default.is_file():
        return default

    candidates = sorted(here.glob("*.ionapi"))
    if candidates:
        return candidates[0]

    mcp_install = Path.home() / "compass-mcp" / "credentials.ionapi"
    if mcp_install.is_file():
        return mcp_install

    raise FileNotFoundError(
        "No .ionapi file found. Set IONAPI_FILE, place credentials.ionapi "
        f"next to {here}, or install compass-mcp first (this tool also looks "
        "for ~/compass-mcp/credentials.ionapi)."
    )


class IonApiConfig:
    """Parsed .ionapi file plus the derived URLs we need."""

    def __init__(self, raw: dict[str, Any]):
        self.tenant = raw["ti"]
        self.client_id = raw["ci"]
        self.client_secret = raw["cs"]
        self.saak = raw["saak"]
        self.sask = raw["sask"]

        ion_base = raw["iu"].rstrip("/")

        pu = raw["pu"].rstrip("/")
        ot = raw["ot"].lstrip("/")
        self.token_url = f"{pu}/{ot}"

        self.compass_base = os.environ.get(
            "COMPASS_BASE_URL",
            f"{ion_base}/{self.tenant}/DATAFABRIC/compass/v2",
        ).rstrip("/")

    @classmethod
    def load(cls, path: Path) -> "IonApiConfig":
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        missing = [k for k in ("ti", "ci", "cs", "saak", "sask", "iu", "pu", "ot") if k not in raw]
        if missing:
            raise ValueError(f"{path} is missing required keys: {missing}")
        return cls(raw)


class TokenManager:
    def __init__(self, cfg: IonApiConfig):
        self.cfg = cfg
        self._lock = threading.Lock()
        self._token: str | None = None
        self._expires_at: float = 0.0

    def get_token(self, client: httpx.Client) -> str:
        with self._lock:
            if self._token and time.time() < self._expires_at - 60:
                return self._token
            return self._refresh(client)

    def _refresh(self, client: httpx.Client) -> str:
        data = {
            "grant_type": "password",
            "client_id": self.cfg.client_id,
            "client_secret": self.cfg.client_secret,
            "username": self.cfg.saak,
            "password": self.cfg.sask,
        }
        resp = client.post(
            self.cfg.token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"OAuth token request failed ({resp.status_code}): {resp.text[:500]}"
            )
        payload = resp.json()
        token = payload.get("access_token")
        if not token:
            raise RuntimeError(f"No access_token in token response: {payload}")
        self._token = token
        self._expires_at = time.time() + float(payload.get("expires_in", 3600))
        return token


class PageTooLargeError(RuntimeError):
    """Raised when Compass rejects a result page for exceeding its size cap."""


class CompassClient:
    def __init__(self, cfg: IonApiConfig, tokens: TokenManager):
        self.cfg = cfg
        self.tokens = tokens
        self.client = httpx.Client(timeout=HTTP_TIMEOUT)

    def _auth_headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self.tokens.get_token(self.client)}"}
        if extra:
            headers.update(extra)
        return headers

    def ping(self) -> dict[str, Any]:
        url = f"{self.cfg.compass_base}/ping"
        resp = self.client.get(url, headers=self._auth_headers())
        ok = resp.status_code == 200
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return {"ok": ok, "status_code": resp.status_code, "response": body}

    def submit(self, sql: str) -> str:
        """Submit SQL, return the queryId."""
        url = f"{self.cfg.compass_base}/jobs/"
        resp = self.client.post(
            url,
            content=sql.encode("utf-8"),
            headers=self._auth_headers(
                {"Content-Type": "text/plain", "Accept": "application/json"}
            ),
        )
        if resp.status_code not in (200, 201, 202):
            raise RuntimeError(
                f"Failed to submit query ({resp.status_code}): {resp.text[:500]}"
            )
        query_id = None
        try:
            data = resp.json()
            query_id = (
                data.get("queryId")
                or data.get("id")
                or data.get("query_id")
                or data.get("jobId")
            )
        except Exception:
            pass
        if not query_id:
            loc = resp.headers.get("Location", "")
            if loc:
                query_id = loc.rstrip("/").split("/")[-1]
        if not query_id:
            raise RuntimeError(
                f"Could not determine queryId from submit response: "
                f"{resp.text[:500]} | headers={dict(resp.headers)}"
            )
        return query_id

    def status(self, query_id: str) -> dict[str, Any]:
        url = f"{self.cfg.compass_base}/jobs/{query_id}/status/"
        resp = self.client.get(url, headers=self._auth_headers({"Accept": "application/json"}))
        if resp.status_code not in (200, 201, 202):
            raise RuntimeError(
                f"Failed to get status ({resp.status_code}): {resp.text[:500]}"
            )
        return resp.json()

    def result_page(self, query_id: str, offset: int, limit: int) -> list[Any]:
        """Fetch one page of results as a list of row dicts.

        Raises PageTooLargeError if the page exceeds Compass's ~10MB cap so
        callers can retry with a smaller limit.
        """
        url = f"{self.cfg.compass_base}/jobs/{query_id}/result/"
        resp = self.client.get(
            url,
            params={"offset": offset, "limit": limit},
            headers=self._auth_headers({"Accept": "application/json"}),
        )
        if resp.status_code == 400:
            body_text = resp.text
            if f'"messageCode":"{PAGE_TOO_LARGE_CODE}"' in body_text or "too large to process" in body_text:
                raise PageTooLargeError(body_text[:300])
            raise RuntimeError(f"Failed to fetch result ({resp.status_code}): {body_text[:500]}")
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch result ({resp.status_code}): {resp.text[:500]}")
        data = resp.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("results", "data", "records", "items", "rows"):
                if isinstance(data.get(key), list):
                    return data[key]
        return []

    def result(self, query_id: str, max_rows: int) -> dict[str, Any]:
        """Single-page fetch (used for small previews / error detail)."""
        rows = self.result_page(query_id, 0, max_rows)
        return {"format": "json", "data": rows}

    def _error_detail(self, query_id: str, status_obj: dict[str, Any]) -> str:
        try:
            res = self.result(query_id, 50)
            data = res.get("data")
            rows = data if isinstance(data, list) else []
            msgs = []
            for row in rows:
                if isinstance(row, dict):
                    m = row.get("message") or row.get("localizedMessage")
                    if m:
                        msgs.append(m)
            if msgs:
                return " | ".join(msgs)
        except Exception:
            pass
        return status_obj.get("message") or json.dumps(status_obj)

    def wait_for_finish(
        self,
        query_id: str,
        timeout: float = POLL_TIMEOUT,
        poll_interval: float = POLL_INTERVAL,
        should_cancel=None,
    ) -> dict[str, Any]:
        """Poll status until FINISHED/FAILED. Returns the final status object."""
        deadline = time.time() + timeout
        while True:
            if should_cancel and should_cancel():
                raise InterruptedError("cancelled")
            st = self.status(query_id)
            state = (
                st.get("status") or st.get("state") or st.get("jobStatus") or ""
            ).upper()
            if state in ("FINISHED", "COMPLETED", "SUCCESS", "SUCCEEDED"):
                return st
            if state in ("FAILED", "CANCELED", "CANCELLED", "ERROR"):
                raise RuntimeError(f"Query {state}: {self._error_detail(query_id, st)}")
            if time.time() > deadline:
                raise TimeoutError(
                    f"Query timed out after {timeout}s (last status: {state or 'unknown'}, queryId: {query_id})"
                )
            time.sleep(poll_interval)

    def run_query(self, sql: str, max_rows: int) -> dict[str, Any]:
        """Submit + wait + fetch a single page. Used for previews."""
        query_id = self.submit(sql)
        final_st = self.wait_for_finish(query_id)
        res = self.result(query_id, max_rows)
        cols_meta = final_st.get("columns")
        status_columns = None
        if isinstance(cols_meta, list):
            status_columns = [
                c.get("name", c) if isinstance(c, dict) else c for c in cols_meta
            ]
        return {
            "query_id": query_id,
            "status": final_st.get("status"),
            "row_count": final_st.get("rowCount"),
            "status_columns": status_columns,
            **res,
        }

    def iter_all_rows(
        self,
        query_id: str,
        total_rows: int,
        page_size: int = DEFAULT_PAGE_SIZE,
        should_cancel=None,
    ):
        """Yield (offset, rows) pages until every row has been fetched.

        Adapts the page size down (never back up) if Compass rejects a page
        for being too large, so wide tables don't need a manually-tuned size.
        """
        offset = 0
        size = page_size
        while offset < total_rows:
            if should_cancel and should_cancel():
                raise InterruptedError("cancelled")
            try:
                rows = self.result_page(query_id, offset, size)
            except PageTooLargeError:
                if size <= MIN_PAGE_SIZE:
                    raise RuntimeError(
                        f"Result page too large even at the minimum page size ({MIN_PAGE_SIZE} rows)."
                    )
                size = max(MIN_PAGE_SIZE, size // 2)
                continue
            if not rows:
                break
            yield offset, rows
            offset += len(rows)


# --------------------------------------------------------------------------- #
# Row normalization
# --------------------------------------------------------------------------- #

def rows_to_columns_and_values(rows: list[Any], status_columns: list[str] | None = None) -> tuple[list[str], list[list[Any]]]:
    """Flatten a list of row-dicts (or row-lists) into (columns, list-of-value-lists)."""
    if not rows:
        return (status_columns or []), []
    if isinstance(rows[0], dict):
        columns = status_columns or list(rows[0].keys())
        values = [[row.get(c) for c in columns] for row in rows]
        return columns, values
    # Already a list of lists.
    return (status_columns or []), rows


def get_client(config_dir: Path | None = None) -> CompassClient:
    """Build a fresh CompassClient from the .ionapi file (no caching)."""
    cfg = IonApiConfig.load(find_ionapi_file(config_dir))
    return CompassClient(cfg, TokenManager(cfg))
