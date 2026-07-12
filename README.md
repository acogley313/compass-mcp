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
  (Windows: tick **"Add Python to PATH"** during install)
- **Claude Desktop**
- A **service-account `.ionapi` credentials file** for your Infor tenant. Get
  one from your Infor ION API administrator, or generate it yourself:
  Infor OS Portal → **API Gateway** → **Authorized Apps** → create/select an
  app → **Download credentials**. It downloads as a `.ionapi` file.

## Quick start

1. **Download this repo** — click the green **Code** button above → **Download ZIP**
   — and unzip it anywhere (e.g. Desktop or Downloads).
2. Drop your `.ionapi` file into the unzipped folder and rename it to
   `credentials.ionapi`.
3. Run the installer:
   - **macOS:** double-click `install.command`
   - **Windows:** double-click `install.bat`

   This copies the folder to your home directory, builds an isolated Python
   environment, verifies it can connect to Compass, and registers the server
   with Claude Desktop — all in one pass.
4. **Fully quit and reopen Claude Desktop** (not just close the window —
   quit it completely so it reloads its MCP server list).
5. Try it in a chat:
   > *"Ping Compass to make sure it's connected."*
   >
   > *"Query Compass: select the first 10 rows from \<your table\>."*

> **Windows SmartScreen note:** the first time you run `install.bat`, Windows
> may show a blue **"Windows protected your PC"** warning, because it's a
> script downloaded from the internet. Click **More info → Run anyway**.
> This is standard for any unsigned script and not a sign anything is wrong.

## Tools exposed to Claude

- **`query_compass(sql, max_rows=1000)`** — run a SQL query, return `columns`
  and `rows` (plus `row_count`, `truncated`, `query_id`). Failed queries return
  a clear `error` + `message`.
- **`export_compass_to_excel(sql, filename="compass_export", rows_per_file=500000)`**
  — run a SQL query in full and stream every row straight into one or more
  `.xlsx` files in your Downloads folder, instead of returning rows in chat.
  Claude calls this automatically instead of `query_compass` when a result is
  (or looks like it'll be) too big for chat. Streams to disk page-by-page
  (never holding the full result in memory) and auto-splits into
  `_part1.xlsx`, `_part2.xlsx`, etc. once a result exceeds the rows-per-file
  setting — this is what makes multi-hundred-thousand-row exports practical.
- **`ping_compass()`** — check Compass connectivity/auth. Returns
  `{"ok": true, "response": "pong"}` when healthy.

## Using this in a Claude Project

Two files are included to make Claude noticeably better at writing CSD/SX.e
SQL out of the box, meant to be attached to a **Claude Project** alongside
this MCP server:

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

Neither file is required for the MCP server itself to work — they're optional
but recommended context for a Claude Project built around it.

## What's in this folder

| File | Purpose |
|------|---------|
| `server.py` | The MCP server (Python, uses the official MCP SDK + httpx) |
| `compass_client.py` | Shared Compass API client — auth, submit/poll/paginate |
| `exporter.py` | Orchestrates a full query run (submit → poll → paginate → write) for `export_compass_to_excel` |
| `excel_writer.py` | Streaming, auto-splitting `.xlsx` writer used by `exporter.py` |
| `install.command` / `install.bat` | One-click installer (recommended — see Quick start) |
| `setup.sh` / `setup.bat` | Builds the venv in place, without touching Claude Desktop's config (see Manual setup) |
| `_register_claude.py` | Registers/updates the `compass` entry in Claude Desktop's config; used by the installers |
| `requirements.txt` | Python dependencies |
| `.env.example` | Optional configuration overrides (none required) |
| `SX_Dictionary_AI_v3.md` | CSD/SX.e table & field reference — optional Claude Project Knowledge file (see above) |
| `compass-query-agent-instructions.md` | Starting-point Claude Project Instructions template (see above) |
| `credentials.ionapi` | **You provide this** — your own Infor ION API service-account credentials. Never commit it; see Security below. |

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
| Tools don't appear in Claude | Fully quit & reopen Claude Desktop; check the config JSON is valid and paths are absolute. |
| Windows: "python is not recognized" | Install Python from python.org and tick "Add Python to PATH", then try again. |
| Windows: installer says the `python` shortcut just opens the Microsoft Store | A real Python isn't installed — only the Store's app-execution alias is on PATH. Install Python from python.org (ticking "Add Python to PATH"), or disable the alias under Settings → Apps → Advanced app settings → App execution aliases. |
| `OAuth token request failed` | Credentials expired/revoked. Re-download the `.ionapi` from the Infor ION API portal and replace `credentials.ionapi`. |
| `No .ionapi file found` | Ensure `credentials.ionapi` sits next to `server.py`, or set `IONAPI_FILE`. |
| Query `timeout` | Increase `COMPASS_POLL_TIMEOUT`. |
| Verify from terminal | `./.venv/bin/python server.py --selftest` |
| `export_compass_to_excel` fails partway through a huge query | Compass jobs can expire if left idle too long between pages; re-run the export. If it keeps happening on the same query, try a smaller `rows_per_file` so pages write to disk faster. |

## License

[MIT](LICENSE)
