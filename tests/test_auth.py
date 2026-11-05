"""Tests for OAuth2 grant selection and scope handling in compass_client.

No network: token endpoints are faked with httpx.MockTransport.
Run:  python -m pytest tests/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compass_client import (  # noqa: E402
    CompassClient,
    IonApiConfig,
    TokenManager,
    parse_scopes,
    resolve_grant,
)

BASE = {
    "ti": "TENANT_TRN",
    "cn": "test app",
    "ci": "TENANT_TRN~client",
    "cs": "client-secret",
    "iu": "https://ion.example.com",
    "pu": "https://sso.example.com:443/TENANT_TRN/as/",
    "oa": "authorization.oauth2",
    "ot": "token.oauth2",
}
PASSWORD_FILE = {**BASE, "saak": "svc-key", "sask": "svc-secret", "v": "1.0"}
CC_FILE = {**BASE, "gt": "client_credentials", "sc": ["Infor-DataFabric"], "v": "1.1"}


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in ("COMPASS_OAUTH_SCOPE", "COMPASS_OAUTH_SCOPE_TRN",
                "COMPASS_BASE_URL", "COMPASS_BASE_URL_TRN"):
        monkeypatch.delenv(var, raising=False)


def write(tmp_path, raw) -> Path:
    p = tmp_path / "x.ionapi"
    p.write_text(json.dumps(raw))
    return p


def token_client(response: httpx.Response | dict, seen: list | None = None) -> httpx.Client:
    """httpx client whose every request returns *response*; records form bodies in *seen*."""
    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append({k: v[0] for k, v in parse_qs(request.content.decode()).items()})
        if isinstance(response, httpx.Response):
            return response
        return httpx.Response(200, json=response)
    return httpx.Client(transport=httpx.MockTransport(handler))


# --- parse_scopes -----------------------------------------------------------

def test_parse_scopes_accepts_list_string_none():
    assert parse_scopes(["A", "B"]) == ["A", "B"]
    assert parse_scopes("A  B\tC") == ["A", "B", "C"]
    assert parse_scopes(None) == []
    assert parse_scopes("") == []
    assert parse_scopes(["A", "A", " B "]) == ["A", "B"]


def test_parse_scopes_rejects_other_types():
    with pytest.raises(ValueError):
        parse_scopes(5)


# --- grant resolution -------------------------------------------------------

def test_grant_from_gt():
    assert resolve_grant({"gt": "client_credentials"}) == "client_credentials"
    assert resolve_grant({"gt": " Password "}) == "password"


def test_legacy_file_without_gt_is_password():
    assert resolve_grant(PASSWORD_FILE) == "password"


def test_no_gt_and_no_service_account_is_an_error():
    with pytest.raises(ValueError, match="cannot tell which OAuth2 grant"):
        resolve_grant(BASE)


def test_unsupported_gt():
    with pytest.raises(ValueError, match="unsupported grant type"):
        resolve_grant({"gt": "authorization_code"})


# --- config loading ---------------------------------------------------------

def test_client_credentials_file_loads_without_service_account(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    assert cfg.grant_type == "client_credentials"
    assert cfg.saak is None and cfg.sask is None
    assert cfg.scopes == ["Infor-DataFabric"]
    assert cfg.token_url == "https://sso.example.com:443/TENANT_TRN/as/token.oauth2"


def test_legacy_password_file_unchanged(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, PASSWORD_FILE))
    assert cfg.grant_type == "password"
    assert (cfg.saak, cfg.sask) == ("svc-key", "svc-secret")
    assert cfg.scopes == []


def test_password_gt_without_service_account_fails(tmp_path):
    with pytest.raises(ValueError, match="password grant requires"):
        IonApiConfig.load(write(tmp_path, {**BASE, "gt": "password"}))


def test_missing_base_keys_still_reported(tmp_path):
    raw = {k: v for k, v in CC_FILE.items() if k != "cs"}
    with pytest.raises(ValueError, match="missing required keys"):
        IonApiConfig.load(write(tmp_path, raw))


def test_load_errors_name_the_file(tmp_path):
    p = write(tmp_path, {**BASE, "gt": "bogus"})
    with pytest.raises(ValueError, match="x.ionapi"):
        IonApiConfig.load(p)


def test_gt_client_credentials_ignores_leftover_service_account(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, {**PASSWORD_FILE, "gt": "client_credentials"}))
    assert cfg.grant_type == "client_credentials"
    assert cfg.saak is None


# --- scope overrides --------------------------------------------------------

def test_env_overrides_file_scope(tmp_path, monkeypatch):
    monkeypatch.setenv("COMPASS_OAUTH_SCOPE", "Only-This")
    cfg = IonApiConfig.load(write(tmp_path, {**CC_FILE, "sc": ["A", "B"]}))
    assert cfg.scopes == ["Only-This"]


def test_empty_env_means_no_scope(tmp_path, monkeypatch):
    monkeypatch.setenv("COMPASS_OAUTH_SCOPE", "")
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    assert cfg.scopes == []


def test_trn_uses_its_own_env_var(tmp_path, monkeypatch):
    monkeypatch.setenv("COMPASS_OAUTH_SCOPE", "Prod-Only")
    monkeypatch.setenv("COMPASS_OAUTH_SCOPE_TRN", "Trn-Only")
    path = write(tmp_path, CC_FILE)
    assert IonApiConfig.load(path, base_url_env="COMPASS_BASE_URL_TRN").scopes == ["Trn-Only"]
    assert IonApiConfig.load(path, base_url_env="COMPASS_BASE_URL").scopes == ["Prod-Only"]


def test_explicit_scope_env_name(tmp_path, monkeypatch):
    monkeypatch.setenv("MY_SCOPE", "Custom")
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE), scope_env="MY_SCOPE")
    assert cfg.scopes == ["Custom"]


# --- token request body -----------------------------------------------------

def test_client_credentials_request_body(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, {**CC_FILE, "sc": ["Infor-DataFabric", "SX"]}))
    seen: list = []
    tm = TokenManager(cfg)
    tm.get_token(token_client({"access_token": "tok", "expires_in": 3600}, seen))
    assert seen == [{
        "grant_type": "client_credentials",
        "client_id": "TENANT_TRN~client",
        "client_secret": "client-secret",
        "scope": "Infor-DataFabric SX",
    }]


def test_password_request_body_has_credentials_and_no_scope(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, PASSWORD_FILE))
    seen: list = []
    TokenManager(cfg).get_token(token_client({"access_token": "tok"}, seen))
    assert seen == [{
        "grant_type": "password",
        "client_id": "TENANT_TRN~client",
        "client_secret": "client-secret",
        "username": "svc-key",
        "password": "svc-secret",
    }]


def test_password_grant_sends_scope_when_sc_present(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, {**PASSWORD_FILE, "sc": ["Infor-DataFabric"]}))
    seen: list = []
    TokenManager(cfg).get_token(token_client({"access_token": "tok"}, seen))
    assert seen[0]["scope"] == "Infor-DataFabric"


def test_no_sc_sends_no_scope(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, {k: v for k, v in CC_FILE.items() if k != "sc"}))
    seen: list = []
    TokenManager(cfg).get_token(token_client({"access_token": "tok"}, seen))
    assert "scope" not in seen[0]


def test_token_is_cached(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    seen: list = []
    client = token_client({"access_token": "tok", "expires_in": 3600}, seen)
    tm = TokenManager(cfg)
    assert tm.get_token(client) == tm.get_token(client) == "tok"
    assert len(seen) == 1


# --- error handling ---------------------------------------------------------

def test_invalid_scope_error_is_readable(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, {**CC_FILE, "sc": ["Nope"]}))
    resp = httpx.Response(400, json={"error": "invalid_scope", "error_description": "bad scope"})
    with pytest.raises(RuntimeError) as ei:
        TokenManager(cfg).get_token(token_client(resp))
    msg = str(ei.value)
    assert "rejected the requested scope" in msg and "Nope" in msg and "bad scope" in msg
    assert "client-secret" not in msg


def test_invalid_scope_in_ions_real_response_shape(tmp_path):
    # Captured from a live ION token endpoint: the scope failure arrives as
    # error=invalid_grant with the real reason in error_description.
    cfg = IonApiConfig.load(write(tmp_path, {**CC_FILE, "sc": ["Infor-DataFabric", "Bogus"]}))
    resp = httpx.Response(400, json={
        "error": "invalid_grant",
        "error_trace_id": "Root=1-abc",
        "error_description": "invalid_scope",
    })
    with pytest.raises(RuntimeError) as ei:
        TokenManager(cfg).get_token(token_client(resp))
    msg = str(ei.value)
    assert "rejected the requested scope" in msg and "Infor-DataFabric Bogus" in msg


def test_invalid_client_error_is_readable(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    resp = httpx.Response(401, json={"error": "invalid_client"})
    with pytest.raises(RuntimeError, match="invalid client credentials"):
        TokenManager(cfg).get_token(token_client(resp))


def test_other_failures_keep_status_and_grant(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    with pytest.raises(RuntimeError, match=r"500, grant: client_credentials"):
        TokenManager(cfg).get_token(token_client(httpx.Response(500, text="boom")))


def test_missing_access_token_does_not_echo_payload(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    with pytest.raises(RuntimeError) as ei:
        TokenManager(cfg).get_token(token_client({"refresh_token": "SECRET-VALUE"}))
    assert "SECRET-VALUE" not in str(ei.value)


# --- granted scope reporting ------------------------------------------------

def test_granted_scope_is_recorded_and_reported(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, {**CC_FILE, "sc": ["A", "B"]}))
    tm = TokenManager(cfg)
    tm.get_token(token_client({"access_token": "t", "scope": "A B"}))
    info = tm.auth_info()
    assert info["scope_granted"] == ["A", "B"]
    assert "warning" not in info


def test_narrowed_scope_warns(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, {**CC_FILE, "sc": ["A", "B"]}))
    tm = TokenManager(cfg)
    tm.get_token(token_client({"access_token": "t", "scope": "A"}))
    assert "B" in tm.auth_info()["warning"]


def test_response_without_scope_is_unknown_not_a_warning(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    tm = TokenManager(cfg)
    tm.get_token(token_client({"access_token": "t"}))
    info = tm.auth_info()
    assert info["scope_granted"] is None and "warning" not in info


def test_ping_includes_auth_info(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("token.oauth2"):
            return httpx.Response(200, json={"access_token": "t", "scope": "Infor-DataFabric"})
        assert request.headers["Authorization"] == "Bearer t"
        return httpx.Response(200, json="pong")

    cc = CompassClient(cfg, TokenManager(cfg))
    cc.client = httpx.Client(transport=httpx.MockTransport(handler))
    out = cc.ping()
    assert out["ok"] is True
    assert out["auth"] == {
        "grant_type": "client_credentials",
        "scope_requested": ["Infor-DataFabric"],
        "scope_granted": ["Infor-DataFabric"],
    }


# --- 401 retry --------------------------------------------------------------

def retrying_client(tmp_path, api_statuses: list[int]):
    """CompassClient whose token endpoint issues tok-1, tok-2, ... and whose API
    answers with *api_statuses* in order (last one repeats).

    Returns (client, token_requests, api_requests) where api_requests holds
    (bearer_token, body) per call.
    """
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    token_requests: list[int] = []
    api_requests: list[tuple[str, bytes]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("token.oauth2"):
            token_requests.append(1)
            return httpx.Response(200, json={"access_token": f"tok-{len(token_requests)}",
                                             "expires_in": 3600})
        api_requests.append((request.headers["Authorization"].removeprefix("Bearer "),
                             request.content))
        status = api_statuses[min(len(api_requests) - 1, len(api_statuses) - 1)]
        return httpx.Response(status, json={"queryId": "q1"} if status == 200 else {"error": "x"})

    cc = CompassClient(cfg, TokenManager(cfg))
    cc.client = httpx.Client(transport=httpx.MockTransport(handler))
    return cc, token_requests, api_requests


def test_401_triggers_one_retry_with_a_fresh_token(tmp_path):
    cc, token_requests, api = retrying_client(tmp_path, [401, 200])
    assert cc.ping()["ok"] is True
    assert len(token_requests) == 2
    assert [t for t, _ in api] == ["tok-1", "tok-2"]


def test_persistent_401_is_retried_only_once(tmp_path):
    cc, token_requests, api = retrying_client(tmp_path, [401])
    out = cc.ping()
    assert out["ok"] is False and out["status_code"] == 401
    assert len(api) == 2 and len(token_requests) == 2


def test_403_scope_violation_is_not_retried(tmp_path):
    cc, token_requests, api = retrying_client(tmp_path, [403])
    assert cc.ping()["status_code"] == 403
    assert len(api) == 1 and len(token_requests) == 1


def test_success_makes_no_extra_token_requests(tmp_path):
    cc, token_requests, api = retrying_client(tmp_path, [200])
    cc.ping(); cc.ping()
    assert len(token_requests) == 1 and len(api) == 2


def test_post_body_is_resent_on_retry(tmp_path):
    cc, _, api = retrying_client(tmp_path, [401, 200])
    assert cc.submit("SELECT 1") == "q1"
    assert [b for _, b in api] == [b"SELECT 1", b"SELECT 1"]
    assert [t for t, _ in api] == ["tok-1", "tok-2"]


def test_invalidate_ignores_a_token_that_is_no_longer_current(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    tm = TokenManager(cfg)
    client = token_client({"access_token": "tok-new", "expires_in": 3600})
    assert tm.get_token(client) == "tok-new"
    tm.invalidate("some-older-token")        # stale caller: must not discard tok-new
    seen: list = []
    assert tm.get_token(token_client({"access_token": "x"}, seen)) == "tok-new"
    assert seen == []                         # served from cache, no new request
    tm.invalidate("tok-new")                  # the current token: now it must refetch
    assert tm.get_token(token_client({"access_token": "tok-3"})) == "tok-3"


# --- password-grant files that carry scopes; migration nudge ----------------

def test_invalid_scope_error_names_the_override_env_var(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, {**CC_FILE, "sc": ["Stale"]}),
                            base_url_env="COMPASS_BASE_URL_TRN")
    resp = httpx.Response(400, json={"error": "invalid_grant", "error_description": "invalid_scope"})
    with pytest.raises(RuntimeError) as ei:
        TokenManager(cfg).get_token(token_client(resp))
    msg = str(ei.value)
    assert "COMPASS_OAUTH_SCOPE_TRN" in msg and "stale" in msg.lower()


def test_stale_sc_on_password_file_can_be_worked_around_with_empty_env(tmp_path, monkeypatch):
    path = write(tmp_path, {**PASSWORD_FILE, "sc": ["Stale"]})
    assert IonApiConfig.load(path).scopes == ["Stale"]
    monkeypatch.setenv("COMPASS_OAUTH_SCOPE", "")
    seen: list = []
    TokenManager(IonApiConfig.load(path)).get_token(token_client({"access_token": "t"}, seen))
    assert "scope" not in seen[0] and seen[0]["grant_type"] == "password"


def test_password_grant_reports_a_migration_notice(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, PASSWORD_FILE))
    info = TokenManager(cfg).auth_info()
    assert "client_credentials is recommended" in info["notice"]


def test_client_credentials_has_no_notice(tmp_path):
    cfg = IonApiConfig.load(write(tmp_path, CC_FILE))
    assert "notice" not in TokenManager(cfg).auth_info()
