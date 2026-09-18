# Changelog

All notable changes to Compass MCP are documented in this file.

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
