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
   with Claude Desktop — all in one pass.

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
   - **Windows, Microsoft Store build of Claude Desktop:** the Store version
     is sandboxed and never sees `%APPDATA%\Claude` — its config instead lives
     at `%LOCALAPPDATA%\Packages\Claude_<hash>\LocalCache\Roaming\Claude\claude_desktop_config.json`
     (the `<hash>` suffix is publisher-specific; there's normally only one
     `Claude_*` folder under `Packages`). `_register_claude.py` (used by the
     installers) already detects this automatically.

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

1. **Auth** — reads `credentials.ionapi`, performs an OAuth2 *password* grant
   against the ION token endpoint (`pu` + `ot`), caches the bearer token and
   refreshes it ~60s before expiry.
2. **Submit** — `POST {base}/jobs/` with the SQL as a plain-text body → returns
   a `queryId`.
3. **Poll** — `GET {base}/jobs/{queryId}/status/` every 2s. Compass returns
   HTTP 202 while `RUNNING` and 201 when `FINISHED`.
4. **Fetch** — `GET {base}/jobs/{queryId}/result/` → rows. The server
   normalizes them into `columns` + `rows`.

The Compass base URL is derived from your `.ionapi` tenant automatically —
there's nothing tenant-specific to configure.

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

## Security

- `credentials.ionapi` contains live secrets for your Infor tenant. **Never
  commit it to git or share it outside your organization.** The included
  `.gitignore` keeps it (and any other `*.ionapi` file) out of version control.
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

## License

[MIT](LICENSE)
