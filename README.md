# Compass MCP Server

A small, self-contained [MCP](https://modelcontextprotocol.io) server that lets
Claude run SQL queries against **Infor Compass** (Data Fabric) directly from
chat. You ask a question, Claude writes the SQL, fires it through this server,
and reads back the results — including automatically exporting large result
sets to Excel when they're too big to show in chat.

It wraps the Compass async query API (submit → poll → fetch) and handles Infor
ION API OAuth2 authentication automatically using your own `.ionapi`
credentials file — nothing Compass-related is hardcoded, so anyone with access
to their own Infor tenant can use this as-is.

## Prerequisites

- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
  (Windows: tick **"Add Python to PATH"** during install). On Windows you can
  skip this: if `install.bat` doesn't find a usable Python, it offers to
  install Python 3.13 for you. The Microsoft Store version of Python can't be
  used — the installer will offer the python.org version instead.
- **Claude Desktop**
- **One or two `.ionapi` credentials files** from your Infor tenant:
  - `credentials.ionapi` — for production (required)
  - `credentials_trn.ionapi` — for training environment (optional)
  
  Get these from your Infor ION API administrator, or generate them yourself:
  Infor OS Portal → **API Gateway** → **Authorized Apps** → create/select an
  app → **Download credentials**. It downloads as a `.ionapi` file. If you need
  access to both environments, you'll need separate credentials for each.

## Quick start

1. **Download this repo** — click the green **Code** button above → **Download ZIP**
   — and unzip it anywhere (e.g. Desktop or Downloads).
2. Drop your credentials file(s) into the unzipped folder:
   - Rename your production credentials to `credentials.ionapi` (required)
   - (Optional) Rename a training credentials file to `credentials_trn.ionapi` if you have access to a training environment
3. Run the installer:
   - **macOS:** double-click `install.command`
   - **Windows:** double-click `install.bat`

   This copies the folder to your home directory, builds an isolated Python
   environment, verifies it can connect to Compass, and registers the server
   with Claude Desktop — all in one pass. Near the end it asks for your CSD
   operator/login code (e.g. `AC01`) — this enables `fetch_csd` and
   `fetch_csd_trn` (see **Two ways to read CSD data** below); leave it blank to
   skip and add it later.

   > **Windows:** use `install.bat`, not `setup.bat` — `setup.bat` only builds
   > the Python environment and doesn't add Compass to Claude Desktop. The
   > Windows installer also closes Claude Desktop while it works (so it can't
   > overwrite the new config) and reopens it at the end.
4. **Fully quit and reopen Claude Desktop** (not just close the window —
   quit it completely so it reloads its MCP server list). On Windows the
   installer does this for you.
5. (Optional but recommended) Set up a Claude Project to manage environment selection:
   - Create a new Claude Project
   - Add the contents of `claude_project_instructions.md` to your Project Instructions
   - This enables Claude to ask which environment you want at the start of each conversation
6. Try it in a chat:
   > *"Ping Compass to make sure it's connected."*
   >
   > *"Query Compass: select the first 10 rows from \<your table\>."*

> **Windows SmartScreen note:** the first time you run `install.bat`, Windows
> may show a blue **"Windows protected your PC"** warning, because it's a
> script downloaded from the internet. Click **More info → Run anyway**.
> This is standard for any unsigned script and not a sign anything is wrong.

## Tools exposed to Claude

This server exposes tools for **two environments**: Production and Training (TRN). Each environment has its own set of tools:

### Production Environment
- **`query_compass(sql, max_rows=1000)`** — run a SQL query against production, return `columns`
  and `rows` (plus `row_count`, `truncated`, `query_id`). Failed queries return
  a clear `error` + `message`.
- **`fetch_csd(table, where="", max_rows=1000)`** — read a table straight from
  the live CSD/SX.e database instead of the Compass datalake replica. No SQL
  (table name + optional WHERE clause, every column comes back), but faster
  and immune to datalake replication lag. See **Two ways to read CSD data**
  below. Requires the one-time `CSD_OPERATOR_INIT` setup described there.
- **`export_csd_to_excel(table, where="", filename="", rows_per_file=100000)`**
  — the Excel export for `fetch_csd`: stream a whole live CSD table (or a
  `where`-filtered slice) into `.xlsx` files in your Downloads folder, e.g.
  every ICSW item, without a SAAMM extract. Every column of the table is
  written. Roughly 900 rows/s on wide tables, so a few hundred thousand rows
  takes several minutes; for huge pulls, filter by warehouse or vendor and
  export in pieces.
- **`export_compass_to_excel(sql, filename="compass_export", rows_per_file=500000)`**
  — run a SQL query in full and stream every row straight into one or more
  `.xlsx` files in your Downloads folder, instead of returning rows in chat.
  Streams to disk page-by-page (never holding the full result in memory) and
  auto-splits into `_part1.xlsx`, `_part2.xlsx`, etc. once a result exceeds
  the rows-per-file setting — this is what makes multi-hundred-thousand-row
  exports practical.
- **`ping_compass()`** — check production Compass connectivity/auth. Returns
  `{"ok": true, "response": "pong"}` when healthy.

### Training (TRN) Environment
- **`query_compass_trn(sql, max_rows=1000)`** — same as `query_compass` but against training
- **`export_compass_to_excel_trn(sql, filename="compass_export", rows_per_file=500000)`** — same as `export_compass_to_excel` but against training
- **`ping_compass_trn()`** — check training Compass connectivity/auth
- **`fetch_csd_trn(table, where="", max_rows=1000)`** — same as `fetch_csd` but against live training CSD (uses `credentials_trn.ionapi`)
- **`export_csd_to_excel_trn(table, where="", filename="", rows_per_file=100000)`** — same as `export_csd_to_excel` but against live training CSD

## Using this in a Claude Project

Several files are included to enhance Claude's Compass query capabilities:

### Environment Management
- **`claude_project_instructions.md`** — **Recommended**: Add this file's contents to your Claude Project's **Project Instructions** to enable seamless environment selection. Claude will ask which environment (Production or Training) you want to use at the start of each conversation, then automatically use the corresponding tools throughout the session. See the file for full instructions.

### Query Optimization (Optional)
- **`SX_Dictionary_AI_v3.md`** — a business-term-to-table/field reference
  covering 64 core CSD tables (customers, orders, inventory, pricing, AP/AR,
  warehouse management, etc.), generated from Infor's CSD data-conversion
  field maps. Add it as a **Project Knowledge** file.
- **`compass-query-agent-instructions.md`** — a starting-point **Project
  Instructions** template: tells Claude to default to writing/running SQL
  rather than asking clarifying questions, lists always-on filters
  (`cono`, `statustype`), and maps plain-language requests ("customers",
  "orders", "inventory") to the right tables. **Fill in the bracketed
  placeholders** (your company name, your warehouse code list) before using
  it — the rest is generic to any CSD/SX.e install.

The environment management file is recommended. The query optimization files are optional but recommended context for a Claude Project built around Compass.

## Two ways to read CSD data

This server can reach CSD data two different ways, and Claude picks between
them based on your request:

|                     | `query_compass`                        | `fetch_csd`                              |
|---------------------|-----------------------------------------|-------------------------------------------|
| Reads from          | Compass datalake (a **replica** of CSD)  | **CSD itself**, live                       |
| Query language      | Full SQL — joins, `SELECT` any columns   | No SQL — one table + optional WHERE clause |
| Columns returned     | Whatever you `SELECT`                    | Every column on the table, always          |
| Speed                | Slower (async job: submit → poll → fetch)| Faster, no polling                         |
| Freshness            | Can lag behind CSD (replication delay)   | Always current                             |

Each has a training twin (`query_compass_trn` / `fetch_csd_trn`) that works
the same way against your `credentials_trn.ionapi` tenant.

Default to `query_compass` — it's the only one that can join tables or pick
columns. Reach for `fetch_csd` when the datalake copy might be stale (a
record was just changed in CSD and Compass hasn't caught up yet) or when you
explicitly want to double-check against CSD directly, e.g.:

> *"Check CSD directly for customer 8221's current price on 4A6H4018 — the*
> *datalake might not have caught up yet."*

WHERE-clause syntax for `fetch_csd` is CSD's own dialect, not SQL — string
literals need **double** quotes (`whse = "TN01"`, not `'TN01'`), and there's
no `WHERE` keyword in the string you pass.

### One-time setup: `CSD_OPERATOR_INIT`

`fetch_csd` needs one more thing than `query_compass`: a CSD operator/login
code (e.g. `AC01`) to run as. This is **per person** — ask whoever
administers CSD operators for yours if you don't already know it, or use
your own login code from CSD.

`install.command`/`install.bat` ask for it during setup (Quick start above),
so on a fresh install there's nothing extra to do. To add or change it later
— e.g. you skipped the prompt, or you're updating an existing install — edit
your `env` block in `claude_desktop_config.json` by hand (same file the
installer set up):

```json
"compass": {
  "command": "/path/to/compass-mcp/.venv/bin/python",
  "args": ["/path/to/compass-mcp/server.py"],
  "env": { "CSD_OPERATOR_INIT": "AC01" }
}
```

Then fully quit and reopen Claude Desktop. Until this is set, `fetch_csd`
returns a clear error telling you to add it — every other tool keeps working
as before.

`fetch_csd_trn` uses the same code by default. If your training operator code
differs from production, also set `CSD_OPERATOR_INIT_TRN` in the same `env`
block. (Company number defaults to `1` for both; override with
`CSD_COMPANY_NUMBER` / `CSD_COMPANY_NUMBER_TRN`.)

## What's in this folder

| File | Purpose |
|------|---------|
| `server.py` | The MCP server (Python, uses the official MCP SDK + httpx) — supports both production and training environments |
| `compass_client.py` | Shared Compass API client — auth, submit/poll/paginate, environment-aware credential discovery |
| `exporter.py` | Orchestrates a full query run (submit → poll → paginate → write) for `export_compass_to_excel` — supports both environments |
| `excel_writer.py` | Streaming, auto-splitting `.xlsx` writer used by `exporter.py` |
| `install.command` / `install.bat` | One-click installer (recommended — see Quick start) |
| `setup.sh` / `setup.bat` | Builds the venv in place, without touching Claude Desktop's config (see Manual setup) |
| `_get_python.bat` | Windows-only: shared Python step for `install.bat`/`setup.bat` — finds Python, or offers to install it |
| `find_python.ps1` | Windows-only: locates a usable Python 3.10+ interpreter (skips the Microsoft Store build) |
| `install_python.ps1` | Windows-only: installs Python 3.13 for the current user (winget, or the python.org installer as a fallback) |
| `claude_desktop.ps1` | Windows-only: closes / restarts Claude Desktop during install (never touches the Claude Code CLI) |
| `_register_claude.py` | Registers/updates the `compass` entry in Claude Desktop's config; used by the installers |
| `requirements.txt` | Python dependencies |
| `.env.example` | Optional configuration overrides (none required) — documents both production and TRN env vars |
| `claude_project_instructions.md` | **Recommended** — Claude Project instructions for environment-aware querying (see Using this in a Claude Project) |
| `SX_Dictionary_AI_v3.md` | CSD/SX.e table & field reference — optional Claude Project Knowledge file (see above) |
| `compass-query-agent-instructions.md` | Starting-point Claude Project Instructions template (see above) |
| `credentials.ionapi` | **You provide this** — your own Infor ION API service-account credentials for production. Never commit it; see Security below. |
| `credentials_trn.ionapi` | **You provide this** — your own Infor ION API service-account credentials for training environment (optional). Never commit it; see Security below. |

## Manual setup

If you'd rather not run the one-click installer, you can do it by hand:

1. Clone or download this repo, and place your `.ionapi` file inside it as
   `credentials.ionapi`.
2. Build the environment:

   **macOS / Linux:**
   ```bash
   cd compass-mcp
   bash setup.sh
   ```

   **Windows:**
   ```bat
   cd compass-mcp
   setup.bat
   ```
   (Answer **N** when it asks whether to run `install.bat` instead.)

   This creates a `.venv`, installs dependencies, and runs a live self-test
   that authenticates and pings Compass. You should see:

   ```
   { "ok": true, "status_code": 200, "response": "pong" }
   ```

3. Note the Python interpreter path it prints at the end, e.g.
   `/path/to/compass-mcp/.venv/bin/python`.
4. Open the Claude Desktop config file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **Windows, Microsoft Store / MSIX build of Claude Desktop** (also what
     WinGet and the current website installer deploy): the app is sandboxed
     and has moved its config more than once. Depending on the version it
     reads one of:
     - `%LOCALAPPDATA%\Claude-Data\claude_<id>\claude_desktop_config.json` (current builds)
     - `%LOCALAPPDATA%\Packages\Claude_<hash>\LocalCache\Roaming\Claude\claude_desktop_config.json` (older builds)

     `_register_claude.py` (used by the installers) writes the `compass` entry
     into every one of these that could apply, plus `%APPDATA%\Claude`, so you
     don't need to work out which one your copy uses. Editing by hand? Use
     **Settings → Developer → Edit Config** in the app, which opens the right file.

   (In Claude Desktop you can also reach it via **Settings → Developer → Edit Config**.)
5. Add a `compass` entry (merge into existing `mcpServers` if present),
   substituting your actual folder path:

   **macOS / Linux:**
   ```json
   {
     "mcpServers": {
       "compass": {
         "command": "/path/to/compass-mcp/.venv/bin/python",
         "args": ["/path/to/compass-mcp/server.py"]
       }
     }
   }
   ```

   **Windows** (note `Scripts\python.exe` and **double** backslashes):
   ```json
   {
     "mcpServers": {
       "compass": {
         "command": "C:\\Users\\you\\compass-mcp\\.venv\\Scripts\\python.exe",
         "args": ["C:\\Users\\you\\compass-mcp\\server.py"]
       }
     }
   }
   ```
6. Fully quit and reopen Claude Desktop.

## Updating an existing install

To pick up a newer version of this tool (e.g. a new release from this repo),
just replace `server.py`, `compass_client.py`, `exporter.py`, and
`excel_writer.py` in your installed folder with the latest versions, then
fully quit and reopen Claude Desktop. Since the server is already registered,
you don't need to touch `claude_desktop_config.json` or re-run the installer
— that step only happens once, the first time.

> **Updating to pick up `fetch_csd` / `fetch_csd_trn` and the `export_csd_to_excel` tools (CSD FetchWhere support):**
> same drop-in replace as above — this release changes `server.py`,
> `compass_client.py` and `exporter.py` (and `_register_claude.py` plus the installers if you
> re-run those). No new dependencies. Then set your `CSD_OPERATOR_INIT`, either
> by re-running the installer (it prompts for it and updates your existing
> config in place) or by adding it to the `env` block in
> `claude_desktop_config.json` by hand — see **One-time setup:
> `CSD_OPERATOR_INIT`** above. For `fetch_csd_trn` you also need your
> `credentials_trn.ionapi` in place, same as the other `_trn` tools. Skipping
> the operator step is harmless: every existing tool keeps working, and the
> fetch tools just return a clear error until it's set.

## Moving to another computer

The whole folder is self-contained. To move it:

1. Copy the folder (the `.venv` does **not** transfer — it has
   machine-specific paths; leave it behind or delete it). This works across
   operating systems.
2. On the new machine, rebuild the venv: `bash setup.sh` (macOS/Linux) or
   `setup.bat` (Windows).
3. Update the paths in the Claude Desktop config to match the new location
   and OS (see the Windows path format above).

`credentials.ionapi` travels with the folder, so there's no re-entering secrets
— just make sure you're not copying it somewhere less secure than where it
started.

## How it works

1. **Auth** — reads `credentials.ionapi`, performs an OAuth2 token request
   against the ION token endpoint (`pu` + `ot`) using the grant the file is set
   up for (see [OAuth grant types and scopes](#oauth-grant-types-and-scopes)),
   caches the bearer token and refreshes it ~60s before expiry.
2. **Submit** — `POST {base}/jobs/` with the SQL as a plain-text body → returns
   a `queryId`.
3. **Poll** — `GET {base}/jobs/{queryId}/status/` every 2s. Compass returns
   HTTP 202 while `RUNNING` and 201 when `FINISHED`.
4. **Fetch** — `GET {base}/jobs/{queryId}/result/` → rows. The server
   normalizes them into `columns` + `rows`.

The Compass base URL is derived from your `.ionapi` tenant automatically —
there's nothing tenant-specific to configure.

`fetch_csd` is a different Infor interface entirely (`SX/rest`, not
`DATAFABRIC/compass`), also derived from the same tenant, using the same
bearer token:

1. **Fetch a page** — `POST {csd_base}/serviceinterface/proxy/FetchWhere` with
   `{CompanyNumber, Operator, TableName, WhereClause, BatchSize, RestartRowID}`.
2. **Read rows** — the response holds them under `ttbl<tablename>` (e.g.
   `ttblicsw`), or `{"NoRecords": ...}` when nothing matches.
3. **Page** — a `RestartRowID` in the response means there's another page;
   feed it back as the next request's `RestartRowID`. Its absence means
   that was the last page.

## Configuration overrides (optional)

All optional — see `.env.example`. Set them as environment variables in the
Claude config's `env` block if needed, e.g. a longer timeout for big queries:

```json
"compass": {
  "command": "/path/to/compass-mcp/.venv/bin/python",
  "args": ["/path/to/compass-mcp/server.py"],
  "env": { "COMPASS_POLL_TIMEOUT": "300", "COMPASS_MAX_ROWS": "5000" }
}
```

`fetch_csd` / `fetch_csd_trn` need `CSD_OPERATOR_INIT` set the same way — see
**One-time setup: `CSD_OPERATOR_INIT`** above.

## OAuth grant types and scopes

The server supports two ION API grant types. Which one is used is decided by
the `.ionapi` file itself, so there is nothing extra to configure:

| `.ionapi` file | Grant used |
|---|---|
| `"gt": "client_credentials"` | **client credentials** — sends only `ci` / `cs`. No service account (`saak`/`sask`) needed. Recommended for new setups and for anyone you share the server with. |
| `"gt": "password"`, or no `gt` but `saak` + `sask` present | **password** — the original behavior. Still supported, but **we recommend moving to client credentials** (see below). |

Create a client-credentials file in ION API → **Authorized Apps** → add an app
with the *Backend Service* / client-credentials option, then **Download
credentials**.

**Moving from password to client credentials.** The password grant needs a
service account's key and secret in the file; client credentials uses only the
app's own client ID and secret, and can be restricted with enforced scopes.
To switch:

1. In ION API → **Authorized Apps**, create a client-credentials app with the
   scopes you need (e.g. `Infor-DataFabric`, plus `Infor-SX` if you use the
   `fetch_csd` tools) and choose to enforce them.
2. Download its credentials and replace `credentials.ionapi` (or
   `credentials_trn.ionapi`) with the new file.
3. Run `python server.py --selftest` (add `--trn` for training) and check it
   shows `Grant type: client_credentials`.

**Scopes.** If the downloaded file has an `sc` list (e.g.
`"sc": ["Infor-DataFabric"]`), those scopes are sent with every token request.
This is needed when the Authorized App *enforces* scopes (a client that doesn't
ask for them is denied) and harmless when it doesn't. Files without `sc` send no
scope, as before. This applies to password-grant files too: one that carries `sc`
now sends it (ION accepts a scope on the password grant). That only matters if the
list is *stale*, e.g. a scope was removed from the app after the file was
downloaded; the resulting `invalid_scope` error says so, and the fix is to
re-download the file or set `COMPASS_OAUTH_SCOPE` (below). Scopes are enforced by
ION, so the app can only ever be given what its Authorized App allows.

To ask for *fewer* scopes than the file lists (for testing, say), set
`COMPASS_OAUTH_SCOPE` (production) or `COMPASS_OAUTH_SCOPE_TRN` (training) to a
space-separated list. Set it to an empty value to send no scope. It can narrow
access but never widen it beyond the Authorized App's scopes.

`ping_compass` and `python server.py --selftest` show the grant type and the
scopes that were requested. (ION's token response doesn't currently echo back a
granted scope, so `scope_granted` shows `null`; if it ever does, a warning
appears when fewer scopes were granted than requested.) A scope the app doesn't
allow produces a readable error that names the scope; a token issued without a
required scope fails at call time with ION's
`403 OAuth2 scopes access control violated`.

A scope limits which *APIs* a token can call. It does not limit which Compass
tables a query can read — use Data Fabric permissions on the Authorized App for
that.

## Security

- `credentials.ionapi` contains live secrets for your Infor tenant. **Never
  commit it to git or share it outside your organization.** The included
  `.gitignore` keeps it (and any other `*.ionapi` file) out of version control.
- When giving the server to someone outside your organization (a vendor, say),
  create a dedicated client-credentials Authorized App for them with enforced
  scopes limited to what they need, and send them only that file — never your
  own `credentials.ionapi`.
- Each person should use their own `.ionapi` file, scoped to whatever
  permissions their Infor admin has granted them — don't pass credentials
  files around between teammates.
- The installers back up your existing `claude_desktop_config.json` (as
  `claude_desktop_config.json.bak`) before modifying it, so a merge issue is
  always recoverable.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tools don't appear in Claude | Fully quit & reopen Claude Desktop; check the config JSON is valid and paths are absolute. Open it from Claude Desktop's **Settings → Developer → Edit Config** to be sure you're editing the file it actually reads. |
| Windows: Settings → Developer shows `compass` **Failed** with `spawn ... ENOENT` | The `command` path in the config doesn't exist — usually because the venv was built somewhere else (e.g. `setup.bat` run in Downloads). Run `install.bat`, which builds it in `%USERPROFILE%\compass-mcp` and registers that path. |
| Windows: "python is not recognized" / Python not found | Run `install.bat` and answer **Y** when it offers to install Python. Or install Python from python.org yourself (tick "Add Python to PATH") and try again. |
| Windows: installer says only the Microsoft Store version of Python is installed | The Store build can't be used here. Let the installer install the python.org version (it can sit alongside the Store one), or install it yourself with `winget install --id Python.Python.3.13 -e --source winget --scope user`. |
| `OAuth token request failed` | Credentials expired/revoked. Re-download the `.ionapi` from the Infor ION API portal and replace `credentials.ionapi`. |
| `No .ionapi file found` | Ensure `credentials.ionapi` sits next to `server.py`, or set `IONAPI_FILE`. |
| Query `timeout` | Increase `COMPASS_POLL_TIMEOUT`. |
| Verify from terminal | `./.venv/bin/python server.py --selftest` (production) or `./.venv/bin/python server.py --selftest --trn` (training) |
| `export_compass_to_excel` fails partway through a huge query | Compass jobs can expire if left idle too long between pages; re-run the export. If it keeps happening on the same query, try a smaller `rows_per_file` so pages write to disk faster. |
| `fetch_csd` returns `config_missing` | Add `CSD_OPERATOR_INIT` to the `env` block in `claude_desktop_config.json` (see **One-time setup** above) and restart Claude Desktop. |
| `fetch_csd` returns `Operator is Invalid. Not On File` | `CSD_OPERATOR_INIT` isn't a valid CSD operator/login code. Double-check it (it's case-insensitive, but must exist in CSD). |
| `fetch_csd` returns a where-clause error | CSD's WHERE dialect isn't SQL — no `SELECT`, and string literals need **double** quotes (`"TN01"`, not `'TN01'`). |

## License

[MIT](LICENSE)
