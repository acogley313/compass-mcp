# Upgrade Instructions for Compass MCP

This document guides existing users through upgrading their Compass MCP installation to the latest version with multi-environment support.

## What's New in This Release

✅ **Dual-environment support** — Query both Production and Training (TRN) environments  
✅ **6 new tools** — 3 tools for each environment (production and TRN variants)  
✅ **Excel exports** — Stream large result sets directly to Excel  
✅ **Improved architecture** — Modularized, maintainable code  
✅ **Smart environment selection** — Optional Claude Project instructions for seamless environment switching  

## Before You Upgrade

### Prerequisites
- Python 3.10+ (same as before)
- Claude Desktop
- Your existing `credentials.ionapi` file (production)
- (Optional) A `credentials_trn.ionapi` file if you have training environment access

### Backup Current Installation
```bash
# macOS / Linux
cp -r ~/compass-mcp ~/compass-mcp.backup

# Windows
xcopy C:\Users\YourName\compass-mcp C:\Users\YourName\compass-mcp.backup /E /I
```

## Upgrade Steps (Simple!)

### 1. Backup Your Existing Installation
```bash
# macOS / Linux
cp -r ~/compass-mcp ~/compass-mcp.backup

# Windows
xcopy %USERPROFILE%\compass-mcp %USERPROFILE%\compass-mcp.backup /E /I
```

### 2. Download and Extract the Release
- Download `compass-mcp-<version>.zip` from GitHub Releases
- Extract directly into your existing `compass-mcp` folder:

```bash
# macOS / Linux
unzip compass-mcp-2.0.0.zip -d ~/compass-mcp

# Windows
tar -xf compass-mcp-2.0.0.zip -C %USERPROFILE%\compass-mcp
# OR use Explorer: right-click zip → Extract All... → browse to compass-mcp folder
```

When prompted to replace existing files, click **Yes to All**.

### 3. Update Python Dependencies
```bash
# macOS / Linux
cd ~/compass-mcp
.venv/bin/pip install -r requirements.txt

# Windows
cd %USERPROFILE%\compass-mcp
.venv\Scripts\pip install -r requirements.txt
```

### 4. (Optional) Add Training Environment Credentials
If you have access to a training environment, copy your credentials file:

```bash
# macOS / Linux
cp <your-trn-credentials>.ionapi ~/compass-mcp/credentials_trn.ionapi

# Windows
copy <your-trn-credentials>.ionapi %USERPROFILE%\compass-mcp\credentials_trn.ionapi
```

### 5. Test the Upgrade
```bash
# macOS / Linux
cd ~/compass-mcp
.venv/bin/python server.py --selftest          # Production
.venv/bin/python server.py --selftest --trn    # Training (if you added TRN creds)

# Windows
cd %USERPROFILE%\compass-mcp
.venv\Scripts\python server.py --selftest      # Production
.venv\Scripts\python server.py --selftest --trn # Training (if you added TRN creds)
```

Expected output:
```
Loading Production credentials...
Token URL:    https://mingle-sso.inforcloudsuite.com/...
Compass base: https://mingle-ionapi.inforcloudsuite.com/.../compass/v2
Pinging Production Compass...
{
  "ok": true,
  "status_code": 200,
  "response": "pong"
}
```

### 6. Restart Claude Desktop
Fully quit and reopen Claude Desktop (not just closing the window — completely quit it).

### 7. (Optional) Update Claude Project Instructions
For the best experience with environment selection:

1. Go to your Claude Project settings
2. Copy the contents of `claude_project_instructions.md` 
3. Paste into your Project Instructions field
4. Save

This enables Claude to ask which environment you want at the start of each conversation.

## Verifying the Upgrade

### Check that all tools are available:
In a Claude chat, you should see these tools available:

**Production:**
- `query_compass`
- `ping_compass`
- `export_compass_to_excel`

**Training (if you added credentials_trn.ionapi):**
- `query_compass_trn`
- `ping_compass_trn`
- `export_compass_to_excel_trn`

### Test connectivity:
```
You: "Ping Compass to verify connectivity."
Claude should call ping_compass() and return "pong"

You: "Ping the training environment."
Claude should call ping_compass_trn() and return "pong" (if available)
```

## Rollback (If Needed)

If you encounter issues, you can rollback to your previous installation:

```bash
# macOS / Linux
rm -rf ~/compass-mcp
mv ~/compass-mcp.backup ~/compass-mcp

# Windows
rmdir /s /q C:\Users\YourName\compass-mcp
move C:\Users\YourName\compass-mcp.backup C:\Users\YourName\compass-mcp
```

Then restart Claude Desktop.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'xlsxwriter'` | Run `.venv/bin/pip install -r requirements.txt` (macOS/Linux) or `.venv\Scripts\pip install -r requirements.txt` (Windows) |
| Tools don't appear in Claude | Fully quit Claude Desktop (not just close) and reopen it. Check that `server.py` is updated. |
| `FileNotFoundError: No .ionapi file found` | Ensure `credentials.ionapi` is in the same folder as `server.py`. For TRN, add `credentials_trn.ionapi` |
| Self-test fails with OAuth error | Your credentials may have expired. Download fresh `.ionapi` files from the Infor ION API portal. |
| TRN tools don't appear | Make sure you added `credentials_trn.ionapi` and restarted Claude Desktop |

## Getting Help

- Check the [README.md](README.md) for more information
- Review [claude_project_instructions.md](claude_project_instructions.md) for environment management setup
- Check the Troubleshooting section in README.md

## What Changed (For Reference)

### New Features
- Multi-environment support (Production + Training)
- 6 tools instead of 3 (one set for each environment)
- Excel export functionality for both environments
- Environment-aware credential discovery
- Claude Project instructions for seamless environment switching

### Files Modified
- `server.py` — Added TRN tools and environment detection
- `compass_client.py` — Parameterized environment support
- `exporter.py` — Environment-aware initialization
- `requirements.txt` — Added xlsxwriter dependency
- `.env.example` — Documented TRN environment variables

### Files Added
- `claude_project_instructions.md` — Recommended Claude Project setup
- `UPGRADE_INSTRUCTIONS.md` — This file

## Success Indicators

After a successful upgrade:
✅ All 3 production tools appear in Claude  
✅ TRN tools appear (if you added credentials_trn.ionapi)  
✅ Self-test passes for production  
✅ Self-test passes for training (if applicable)  
✅ Queries execute without errors  
✅ Excel exports work correctly  
