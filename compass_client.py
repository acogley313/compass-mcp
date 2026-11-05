#!/usr/bin/env python3
"""
Compass API client
===================
Shared connection layer for talking to Infor Compass (Data Fabric). Used by
both the MCP server (server.py) and the desktop query app (app/).

Handles ION API OAuth2 auth (password or client_credentials grant, optional scopes), submitting SQL jobs, polling for completion, and
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

# CSD FetchWhere — see CompassClient.csd_fetch_where_page below.
CSD_FETCHWHERE_PATH = "serviceinterface/proxy/FetchWhere"
DEFAULT_CSD_BATCH_SIZE = int(os.environ.get("CSD_BATCH_SIZE", "500"))


def find_ionapi_file(
    start: Path | None = None,
    env_var: str = "IONAPI_FILE",
    default_name: str = "credentials.ionapi",
) -> Path:
    """Locate an .ionapi credentials file.

    Priority:
      1. The env var named by *env_var* (absolute or relative path, ~ expansion supported)
      2. A file named *default_name* next to this module
      3. (only for default env) the first *.ionapi file next to this module
      4. ~/compass-mcp/credentials.ionapi — the standard install location used
         by install.command/install.bat, so standalone tools (like the Query
         App shared on its own) can find credentials from an existing
         compass-mcp install without needing their own copy.
    """
    env_path = os.environ.get(env_var)
    if env_path:
        p = Path(env_path).expanduser()
        if not p.is_file():
            raise FileNotFoundError(f"{env_var} points to a missing file: {p}")
        return p

    here = (start or Path(__file__).resolve().parent)
    default = here / default_name
    if default.is_file():
        return default

    # Fallback glob only for the production (default) case so TRN doesn't
    # accidentally pick up the wrong file.
    if default_name == "credentials.ionapi":
        candidates = sorted(here.glob("*.ionapi"))
        if candidates:
            return candidates[0]

    mcp_install = Path.home() / "compass-mcp" / default_name
    if mcp_install.is_file():
        return mcp_install

    raise FileNotFoundError(
        f"No .ionapi file found. Set {env_var}, place {default_name} "
        f"next to {here}, or install compass-mcp first (this tool also looks "
        f"for ~/{mcp_install.parent.name}/{default_name})."
    )


GRANT_PASSWORD = "password"
GRANT_CLIENT_CREDENTIALS = "client_credentials"
SUPPORTED_GRANTS = (GRANT_PASSWORD, GRANT_CLIENT_CREDENTIALS)

PASSWORD_GRANT_NOTICE = (
    "Using the OAuth2 password grant. client_credentials is recommended: it needs no "
    "service-account password and can be limited with enforced scopes. See "
    "'OAuth grant types and scopes' in the README."
)


def parse_scopes(value: Any) -> list[str]:
    """Normalize a scope value into a de-duplicated list of scope names.

    The ``sc`` key in an .ionapi file is a JSON list (``["Infor-DataFabric"]``),
    but env overrides and token responses are space-delimited strings
    (RFC 6749). Accept either, plus None.
    """
    if value is None:
        return []
    if isinstance(value, str):
        items = value.split()
    elif isinstance(value, (list, tuple)):
        items = [str(v).strip() for v in value]
    else:
        raise ValueError(f"scope must be a list or string, got {type(value).__name__}")
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return seen


def _default_scope_env(base_url_env: str) -> str:
    """COMPASS_OAUTH_SCOPE for production, COMPASS_OAUTH_SCOPE_TRN for training."""
    return "COMPASS_OAUTH_SCOPE_TRN" if base_url_env.endswith("_TRN") else "COMPASS_OAUTH_SCOPE"


def resolve_grant(raw: dict[str, Any]) -> str:
    """Decide which OAuth2 grant an .ionapi file is meant for.

    ``gt`` wins when present. Older password-grant files have no ``gt`` and are
    recognised by their service-account keys (``saak``/``sask``).
    """
    gt = raw.get("gt")
    if gt:
        grant = str(gt).strip().lower()
        if grant not in SUPPORTED_GRANTS:
            raise ValueError(
                f"unsupported grant type gt={gt!r} (supported: {', '.join(SUPPORTED_GRANTS)})"
            )
        return grant
    if raw.get("saak") and raw.get("sask"):
        return GRANT_PASSWORD
    raise ValueError(
        "cannot tell which OAuth2 grant to use: no 'gt' key and no 'saak'/'sask' "
        "service-account keys (expected gt=client_credentials or a password-grant file)"
    )


class IonApiConfig:
    """Parsed .ionapi file plus the derived URLs we need."""

    def __init__(
        self,
        raw: dict[str, Any],
        base_url_env: str = "COMPASS_BASE_URL",
        csd_base_url_env: str = "CSD_BASE_URL",
        scope_env: str | None = None,
    ):
        self.tenant = raw["ti"]
        self.client_id = raw["ci"]
        self.client_secret = raw["cs"]

        self.grant_type = resolve_grant(raw)
        # Service-account credentials are only used (and only required) for the
        # password grant. A client-credentials file doesn't have them.
        if self.grant_type == GRANT_PASSWORD:
            missing_sa = [k for k in ("saak", "sask") if not raw.get(k)]
            if missing_sa:
                raise ValueError(f"password grant requires keys: {missing_sa}")
            self.saak: str | None = raw["saak"]
            self.sask: str | None = raw["sask"]
        else:
            self.saak = None
            self.sask = None

        # Scopes: ``sc`` in the .ionapi file is sent whenever present (needed
        # if the Authorized App enforces scopes, harmless if it doesn't). An
        # env var, when set, replaces it so a user can narrow what they ask
        # for; set it to an empty value to send no scope at all. ION enforces
        # the app's scopes server-side, so this can narrow access but never
        # widen it.
        self.scopes: list[str] = parse_scopes(raw.get("sc"))
        scope_env = scope_env or _default_scope_env(base_url_env)
        self.scope_env = scope_env
        env_scope = os.environ.get(scope_env)
        if env_scope is not None:
            self.scopes = parse_scopes(env_scope)

        ion_base = raw["iu"].rstrip("/")

        pu = raw["pu"].rstrip("/")
        ot = raw["ot"].lstrip("/")
        self.token_url = f"{pu}/{ot}"

        self.compass_base = os.environ.get(
            base_url_env,
            f"{ion_base}/{self.tenant}/DATAFABRIC/compass/v2",
        ).rstrip("/")

        # CSD FetchWhere (see below) — a completely different Infor interface
        # (SX/rest, not DATAFABRIC/compass) that reads the live CSD database
        # directly, bypassing the Compass datalake replica.
        self.csd_base = os.environ.get(
            csd_base_url_env,
            f"{ion_base}/{self.tenant}/SX/rest",
        ).rstrip("/")

    @classmethod
    def load(
        cls,
        path: Path,
        base_url_env: str = "COMPASS_BASE_URL",
        csd_base_url_env: str = "CSD_BASE_URL",
        scope_env: str | None = None,
    ) -> "IonApiConfig":
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        missing = [k for k in ("ti", "ci", "cs", "iu", "pu", "ot") if k not in raw]
        if missing:
            raise ValueError(f"{path} is missing required keys: {missing}")
        try:
            return cls(
                raw,
                base_url_env=base_url_env,
                csd_base_url_env=csd_base_url_env,
                scope_env=scope_env,
            )
        except ValueError as e:
            raise ValueError(f"{path}: {e}") from None


class TokenManager:
    def __init__(self, cfg: IonApiConfig):
        self.cfg = cfg
        self._lock = threading.Lock()
        self._token: str | None = None
        self._expires_at: float = 0.0
        # Scopes ION reports it actually granted on the last token response
        # (None until a token has been fetched, or if the response omitted it).
        self.granted_scopes: list[str] | None = None

    def get_token(self, client: httpx.Client) -> str:
        with self._lock:
            if self._token and time.time() < self._expires_at - 60:
                return self._token
            return self._refresh(client)

    def invalidate(self, stale_token: str) -> None:
        """Forget *stale_token* so the next get_token() fetches a new one.

        Only clears the cache if it still holds that token, so a request that
        got a 401 can't discard a newer token another thread already fetched.
        """
        with self._lock:
            if self._token == stale_token:
                self._token = None
                self._expires_at = 0.0

    def _request_data(self) -> dict[str, str]:
        data = {
            "grant_type": self.cfg.grant_type,
            "client_id": self.cfg.client_id,
            "client_secret": self.cfg.client_secret,
        }
        if self.cfg.grant_type == GRANT_PASSWORD:
            data["username"] = self.cfg.saak or ""
            data["password"] = self.cfg.sask or ""
        if self.cfg.scopes:
            data["scope"] = " ".join(self.cfg.scopes)
        return data

    def _token_error(self, resp: httpx.Response) -> RuntimeError:
        """Turn a failed token response into a readable error."""
        code = description = None
        try:
            body = resp.json()
            if isinstance(body, dict):
                code = body.get("error")
                description = body.get("error_description")
        except Exception:
            pass
        detail = resp.text[:500]
        # ION reports a rejected scope as error="invalid_grant" with
        # error_description="invalid_scope", not as error="invalid_scope", so
        # look for the marker in both fields.
        marker = f"{code or ''} {description or ''}".lower()
        if "invalid_scope" in marker:
            return RuntimeError(
                f"OAuth token request rejected the requested scope "
                f"{' '.join(self.cfg.scopes) or '(none)'!r} (grant: {self.cfg.grant_type}). "
                f"The Authorized App doesn't permit it — check the 'sc' list in the "
                f".ionapi file (it may be stale if scopes were removed from the app "
                f"after the file was downloaded) and the app's scopes in ION API. "
                f"To override without editing the file, set {self.cfg.scope_env} to a "
                f"narrower space-separated list, or to an empty value to send none. "
                f"Server said: {description or detail}"
            )
        if "invalid_client" in marker:
            return RuntimeError(
                f"OAuth token request failed: invalid client credentials "
                f"(grant: {self.cfg.grant_type}). The .ionapi 'ci'/'cs' may be revoked or "
                f"expired — re-download it from ION API. Server said: {description or detail}"
            )
        return RuntimeError(
            f"OAuth token request failed ({resp.status_code}, grant: {self.cfg.grant_type}): {detail}"
        )

    def _refresh(self, client: httpx.Client) -> str:
        resp = client.post(
            self.cfg.token_url,
            data=self._request_data(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code != 200:
            raise self._token_error(resp)
        payload = resp.json()
        token = payload.get("access_token")
        if not token:
            # Don't echo the payload: it is a token response and may carry secrets.
            raise RuntimeError(
                f"No access_token in token response (keys: {sorted(payload)})"
            )
        self._token = token
        self._expires_at = time.time() + float(payload.get("expires_in", 3600))
        granted = payload.get("scope")
        self.granted_scopes = parse_scopes(granted) if granted is not None else None
        return token

    def auth_info(self) -> dict[str, Any]:
        """Which grant/scopes are in use, for ping/selftest output. No secrets."""
        requested = list(self.cfg.scopes)
        info: dict[str, Any] = {
            "grant_type": self.cfg.grant_type,
            "scope_requested": requested,
            "scope_granted": self.granted_scopes,
        }
        if self.cfg.grant_type == GRANT_PASSWORD:
            info["notice"] = PASSWORD_GRANT_NOTICE
        if self.granted_scopes is not None and requested:
            narrowed = [s for s in requested if s not in self.granted_scopes]
            if narrowed:
                info["warning"] = f"requested scope(s) not granted: {' '.join(narrowed)}"
        return info


class PageTooLargeError(RuntimeError):
    """Raised when Compass rejects a result page for exceeding its size cap."""


class CompassClient:
    def __init__(self, cfg: IonApiConfig, tokens: TokenManager):
        self.cfg = cfg
        self.tokens = tokens
        self.client = httpx.Client(timeout=HTTP_TIMEOUT)

    def _request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send an authenticated request.

        If ION answers 401 (the cached token was revoked, or expired earlier
        than expires_in said), drop that token and retry once with a fresh one.
        Anything else — including a 403 scope violation, which a new token
        can't fix — is returned untouched for the caller to handle.
        """
        for attempt in (1, 2):
            token = self.tokens.get_token(self.client)
            resp = self.client.request(
                method,
                url,
                headers={"Authorization": f"Bearer {token}", **(headers or {})},
                **kwargs,
            )
            if resp.status_code != 401 or attempt == 2:
                return resp
            self.tokens.invalidate(token)
        return resp  # pragma: no cover - loop always returns

    def ping(self) -> dict[str, Any]:
        url = f"{self.cfg.compass_base}/ping"
        resp = self._request("GET", url)
        ok = resp.status_code == 200
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return {
            "ok": ok,
            "status_code": resp.status_code,
            "response": body,
            "auth": self.tokens.auth_info(),
        }

    def submit(self, sql: str) -> str:
        """Submit SQL, return the queryId."""
        url = f"{self.cfg.compass_base}/jobs/"
        resp = self._request(
            "POST",
            url,
            content=sql.encode("utf-8"),
            headers={"Content-Type": "text/plain", "Accept": "application/json"},
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
        resp = self._request("GET", url, headers={"Accept": "application/json"})
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
        resp = self._request(
            "GET",
            url,
            params={"offset": offset, "limit": limit},
            headers={"Accept": "application/json"},
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

    # ----------------------------------------------------------------- #
    # CSD FetchWhere — live reads straight from CSD, bypassing the
    # Compass datalake replica. Same auth, a different Infor interface
    # (SX/rest instead of DATAFABRIC/compass). No SQL: one table, an
    # optional WHERE clause, every column comes back. Fast, and paginates
    # via a RestartRowID the server hands back each page.
    # ----------------------------------------------------------------- #

    def csd_fetch_where_page(
        self,
        table: str,
        where_clause: str,
        restart_row_id: str,
        batch_size: int,
        operator: str,
        company_number: int,
    ) -> dict[str, Any]:
        """One page of a FetchWhere call.

        Returns {"rows": [...], "restart_row_id": str | None}. A `None`
        restart_row_id means this was the last page. String literals in
        `where_clause` must be double-quoted (CSD rejects single quotes).
        """
        url = f"{self.cfg.csd_base}/{CSD_FETCHWHERE_PATH}"
        payload = {
            "CompanyNumber": company_number,
            "Operator": operator,
            "TableName": table,
            "WhereClause": where_clause or "",
            "BatchSize": batch_size,
            "RestartRowID": restart_row_id or "",
        }
        resp = self._request(
            "POST",
            url,
            json=payload,
            headers={"Accept": "application/json"},
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"FetchWhere failed for table {table!r} ({resp.status_code}): {resp.text[:500]}"
            )
        text = resp.text.strip()
        data = json.loads(text) if text else {}
        if data.get("NoRecords"):
            return {"rows": [], "restart_row_id": None}
        rows = data.get(f"ttbl{table.lower()}", [])
        if not isinstance(rows, list):
            rows = []
        return {"rows": rows, "restart_row_id": data.get("RestartRowID")}

    def iter_csd_fetch_where(
        self,
        table: str,
        where_clause: str,
        operator: str,
        company_number: int,
        batch_size: int = DEFAULT_CSD_BATCH_SIZE,
        should_cancel=None,
    ):
        """Yield successive row-batches from FetchWhere until exhausted."""
        restart_row_id = ""
        while True:
            if should_cancel and should_cancel():
                raise InterruptedError("cancelled")
            page = self.csd_fetch_where_page(
                table, where_clause, restart_row_id, batch_size, operator, company_number
            )
            if page["rows"]:
                yield page["rows"]
            restart_row_id = page["restart_row_id"]
            if not restart_row_id:
                break


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


def get_client_for_env(
    env_var: str = "IONAPI_FILE",
    default_name: str = "credentials.ionapi",
    base_url_env: str = "COMPASS_BASE_URL",
    config_dir: Path | None = None,
    csd_base_url_env: str = "CSD_BASE_URL",
    scope_env: str | None = None,
) -> CompassClient:
    """Build a CompassClient for a specific environment (PRD, TRN, etc.).

    Args:
        env_var: Environment variable name for the credentials path (e.g. IONAPI_FILE_TRN)
        default_name: Default credential file name (e.g. credentials_trn.ionapi)
        base_url_env: Environment variable name for Compass base URL override (e.g. COMPASS_BASE_URL_TRN)
        config_dir: Directory to search for credentials (defaults to this module's directory)
        csd_base_url_env: Environment variable name for CSD FetchWhere base URL override (e.g. CSD_BASE_URL_TRN)
        scope_env: Environment variable that overrides the OAuth scope(s) from the .ionapi
            ``sc`` key. Defaults to COMPASS_OAUTH_SCOPE, or COMPASS_OAUTH_SCOPE_TRN when
            base_url_env ends in _TRN.

    Returns:
        A CompassClient configured for the specified environment.
    """
    cfg = IonApiConfig.load(
        find_ionapi_file(config_dir, env_var=env_var, default_name=default_name),
        base_url_env=base_url_env,
        csd_base_url_env=csd_base_url_env,
        scope_env=scope_env,
    )
    return CompassClient(cfg, TokenManager(cfg))
