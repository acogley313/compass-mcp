# Changelog

All notable changes to Compass MCP are documented in this file.

## [Unreleased]

### Added
- **OAuth2 client-credentials grant** — an `.ionapi` file with `"gt": "client_credentials"`
  now works without the `saak`/`sask` service-account keys, so credentials can be issued
  per app (e.g. to a vendor) instead of per service account. Existing password-grant files
  (no `gt`, or `"gt": "password"`) keep working; the one difference is that if such a file
  carries an `sc` list, those scopes are now sent too (see below). Password grant is now
  flagged as deprecated-in-practice: `ping_compass` and `--selftest` recommend moving to
  client credentials.
- **OAuth scopes** — if the `.ionapi` file has an `sc` list, those scopes are sent with the
  token request (required when the Authorized App enforces scopes). `COMPASS_OAUTH_SCOPE` /
  `COMPASS_OAUTH_SCOPE_TRN` can narrow them. `ping_compass` and `--selftest` report the grant
  type and requested/granted scopes; `invalid_scope` and `invalid_client` failures now give a
  readable message.
- **Automatic retry on 401** — if ION rejects the cached token (revoked, or expired early),
  every Compass and CSD request now drops it, fetches a fresh one and retries once instead of
  failing the query. A 403 (e.g. a missing scope) is not retried, since a new token can't fix it.
- **Unit tests** for grant selection, scope handling and token errors (`tests/`, run with
  `python -m pytest tests/` after `pip install -r requirements-dev.txt`).
- **`fetch_csd` / `fetch_csd_trn`** — read a table straight from the live CSD database
  (Infor's FetchWhere service) instead of the Compass datalake replica, for when the
  replica is stale or out of sync. No SQL: a table name plus an optional WHERE clause,
  every column comes back, and it pages automatically. Uses the existing production /
  training `.ionapi` credentials, plus a per-person `CSD_OPERATOR_INIT` (training can
  override with `CSD_OPERATOR_INIT_TRN`). The installers now offer to set it.
- **`export_csd_to_excel` / `export_csd_to_excel_trn`** — the Excel export for the fetch tools:
  stream a whole live CSD table (or a `where` slice) into auto-splitting `.xlsx` files in
  Downloads, e.g. all ICSW items without a SAAMM extract. Writes every column; defaults to
  100,000 rows per file since the files are wide.

### Fixed
- **Windows: `compass` not showing up in Microsoft Store / MSIX Claude Desktop after install** —
  current Store builds moved their config to `%LOCALAPPDATA%\Claude-Data\claude_<id>\` and
  ignore the older `Packages\Claude_*\LocalCache` copy, so the installer was writing to a
  file the app no longer reads. The registration script now writes the entry to every
  location a Windows install might read (Claude-Data, the packaged LocalCache copy, and
  `%APPDATA%\Claude`), creating the file where needed, and lists each one it updated.
- **Settings not landing when Claude Desktop has more than one config file** (e.g. both the
  classic `%APPDATA%` copy and a Store-packaged copy) — the registration script now updates
  every Claude Desktop config that already exists instead of guessing which one the running
  app reads, so a new `compass` entry or `CSD_OPERATOR_INIT` can't end up in the wrong file.
- **Windows installer on machines with the Microsoft Store Python** — `install.bat` no
  longer dead-ends with "Python not found". It now offers to install Python 3.13 for the
  current user (winget, falling back to the python.org installer), and also finds the
  newer python.org "Python install manager" runtimes.
- **`" "` is not recognized / Could not create venv** — stray non-path output from
  `find_python.ps1` was being used as the Python path.
- **`install.bat` quitting right after installing dependencies** — an unescaped `)` in an
  error message ended its `if` block early, so the `pause`/`exit` after it always ran.
- **Compass missing from Claude Desktop after a "successful" install** — the installer now
  force-closes Claude Desktop before rebuilding the venv and editing its config (so Claude
  can't overwrite the change or hold the old venv open), verifies the entry was written,
  refuses to register paths that don't exist, and reopens Claude Desktop at the end.

### Changed
- `setup.bat` now explains that it doesn't configure Claude Desktop and offers to run
  `install.bat` instead.

## [2.0.0] - 2026-09-18

### Added
- **Multi-environment support** — Query both Production and Training (TRN) Compass environments
- **6 new MCP tools** — Production and TRN variants:
  - `query_compass()` / `query_compass_trn()` — Run SQL queries
  - `ping_compass()` / `ping_compass_trn()` — Check connectivity
  - `export_compass_to_excel()` / `export_compass_to_excel_trn()` — Export to Excel
- **Excel export functionality** — Stream large result sets directly to `.xlsx` files with auto-splitting
- **Parameterized environment support** in `compass_client.py`:
  - `get_client_for_env()` factory function
  - Environment-aware credential discovery with `find_ionapi_file(env_var, default_name)`
  - Support for `IONAPI_FILE` / `IONAPI_FILE_TRN` and `COMPASS_BASE_URL` / `COMPASS_BASE_URL_TRN`
- **Smart environment selection** with `claude_project_instructions.md`
- **Self-test for both environments** — `python server.py --selftest [--trn]`
- **Comprehensive documentation**:
  - `claude_project_instructions.md` — Claude Project setup for environment management
  - `UPGRADE_INSTRUCTIONS.md` — Guide for upgrading existing installations
  - `CHANGELOG.md` — This file
  - Updated README.md with dual-environment setup

### Changed
- **Modularized architecture** (from single `server.py` monolith):
  - `compass_client.py` — Reusable Compass API client with environment awareness
  - `exporter.py` — Bulk export orchestration with environment support
  - `excel_writer.py` — Streaming `.xlsx` writer with auto-splitting
- **Server registration** — MCP server now exposes 6 tools (3 production, 3 TRN)
- **Environment variables** — Added support for TRN-specific overrides:
  - `IONAPI_FILE_TRN` — Path to training credentials
  - `COMPASS_BASE_URL_TRN` — Training Compass base URL override
- **Credential files** — Now support both `credentials.ionapi` and `credentials_trn.ionapi`
- **Self-test output** — More detailed, shows both token URL and Compass base URL

### Improved
- **Error handling** — More descriptive error messages for missing credentials
- **Token management** — Thread-safe token caching with auto-refresh
- **Result pagination** — Adaptive page sizing that auto-downscales for wide tables
- **Code organization** — Clear separation of concerns between client, exporter, and server

### Documentation
- Updated README.md with multi-environment sections
- Added prerequisites for both production and training credentials
- Quick start now includes Claude Project setup steps
- File listing documents all new files
- Troubleshooting updated with TRN environment tests

### Backward Compatibility
✅ Existing single-environment setups continue to work  
✅ Default parameters unchanged  
✅ `get_client()` and `CompassExporter()` work as before  
✅ Production tools are the primary tools (no `_prod` suffix needed)  

### Known Limitations
- Compass query timeout defaults to 120 seconds; override with `COMPASS_POLL_TIMEOUT`
- Result pages capped at ~10MB; exporter automatically downscales on oversized pages
- Excel sheets limited to 1,048,576 rows per sheet; exporter auto-splits across files

### Migration Path
Users upgrading from v1.x → v2.0:
1. Existing production tools work as-is
2. Optional: Add `credentials_trn.ionapi` to enable TRN tools
3. Recommended: Update Claude Project Instructions for environment selection
4. See `UPGRADE_INSTRUCTIONS.md` for detailed steps

---

## [1.0.0] - 2026-06-16

### Features
- Single environment (production) support
- `query_compass()` — Run SQL queries
- `ping_compass()` — Check connectivity
- Basic result normalization
- Manual setup and CLI self-test

---

## Roadmap (Future Releases)

Potential enhancements for future versions:
- [ ] Single unified tool that takes environment as parameter
- [ ] Query result caching
- [ ] Query history/audit logging
- [ ] Scheduled query execution
- [ ] More export formats (CSV, JSON, Parquet)
- [ ] Query performance analytics
- [ ] Advanced filtering UI

---

For more information, see:
- [README.md](README.md) — Main documentation
- [UPGRADE_INSTRUCTIONS.md](UPGRADE_INSTRUCTIONS.md) — Upgrade guide
- [claude_project_instructions.md](claude_project_instructions.md) — Claude Project setup
