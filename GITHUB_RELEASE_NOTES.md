# GitHub Release Instructions

This document explains how to create and publish a release for Compass MCP on GitHub.

## Before Creating a Release

1. **Ensure all changes are committed and pushed**
   ```bash
   git status
   git push origin main
   ```

2. **Verify version numbers are consistent**
   - Update version in any version files (if applicable)
   - Version is typically in format: `X.Y.Z` (e.g., `2.0.0`)

3. **Run final tests**
   ```bash
   .venv/bin/python server.py --selftest
   .venv/bin/python server.py --selftest --trn
   ```

## Creating the Release Zip

The release script creates a **flat zip structure** (no root folder) so users can extract directly into their existing `compass-mcp` folder.

### On macOS/Linux:
```bash
bash build-release.sh 2.0.0
```

This creates `dist/compass-mcp-2.0.0.zip` (201 KB, flat structure).

### On Windows:
```batch
build-release.bat 2.0.0
```

This creates `dist\compass-mcp-2.0.0.zip` (flat structure).

**Note:** Requires 7-Zip or PowerShell. If using PowerShell:
```powershell
Compress-Archive -Path . -DestinationPath 'compass-mcp-2.0.0.zip' -Exclude '*.ionapi', '.venv', '.git', '__pycache__'
```

## Uploading to GitHub

### Via GitHub Web Interface (Easiest)

1. Go to your GitHub repository
2. Click **Releases** (right sidebar)
3. Click **Draft a new release**
4. Fill in the form:
   - **Tag version:** `v2.0.0` (include the `v` prefix)
   - **Release title:** `Compass MCP 2.0.0 - Multi-Environment Support`
   - **Description:** Copy from `CHANGELOG.md` or use template below
   - **Upload binaries:** Drag and drop `dist/compass-mcp-2.0.0.zip` here
5. Choose **Publish release**

### Release Description Template

```markdown
## What's New

✅ **Dual-environment support** — Query both Production and Training (TRN)  
✅ **Excel export** — Stream large result sets to Excel  
✅ **Smart environment selection** — Claude Project instructions included  
✅ **Modularized architecture** — Better code organization  

## Installation

**New users:** Download the zip, unzip, and follow the README.md Quick Start guide.

**Existing users:** See UPGRADE_INSTRUCTIONS.md for a safe upgrade path.

## What Changed

- Added `query_compass_trn()`, `ping_compass_trn()`, `export_compass_to_excel_trn()`
- Support for both `credentials.ionapi` and `credentials_trn.ionapi`
- New `claude_project_instructions.md` for seamless environment selection
- Improved architecture with modularized client and exporter

## Installation Files

- `dist/compass-mcp-2.0.0.zip` — Complete release package (excludes credentials)

## Documentation

- 📖 [README.md](https://github.com/yourorg/compass-mcp/blob/v2.0.0/README.md) — Full documentation
- 📖 [UPGRADE_INSTRUCTIONS.md](https://github.com/yourorg/compass-mcp/blob/v2.0.0/UPGRADE_INSTRUCTIONS.md) — Upgrade guide
- 📖 [CHANGELOG.md](https://github.com/yourorg/compass-mcp/blob/v2.0.0/CHANGELOG.md) — Detailed changelog
- 📖 [claude_project_instructions.md](https://github.com/yourorg/compass-mcp/blob/v2.0.0/claude_project_instructions.md) — Claude Project setup

## Verification

Both environments have been tested:
- ✅ Production Compass connectivity
- ✅ Training (TRN) Compass connectivity
- ✅ OAuth authentication
- ✅ SQL query execution
- ✅ Excel export with auto-splitting
- ✅ Self-test for both environments

## Getting Help

- Check the [README.md](README.md) troubleshooting section
- Review [UPGRADE_INSTRUCTIONS.md](UPGRADE_INSTRUCTIONS.md) if upgrading
- Follow [claude_project_instructions.md](claude_project_instructions.md) for Claude Project setup
```

### Via GitHub CLI (Advanced)

```bash
# Create and publish release in one command
gh release create v2.0.0 \
  -t "Compass MCP 2.0.0 - Multi-Environment Support" \
  -F CHANGELOG.md \
  dist/compass-mcp-2.0.0.zip

# Or create a draft first
gh release create v2.0.0 \
  -t "Compass MCP 2.0.0 - Multi-Environment Support" \
  -F CHANGELOG.md \
  --draft \
  dist/compass-mcp-2.0.0.zip
```

## After Publishing

### Share with Users

1. **Internal communication:**
   - Post the release link in Slack/email
   - Direct users to `UPGRADE_INSTRUCTIONS.md` for existing installs
   - Point new users to the README.md Quick Start

2. **Documentation:**
   - Update any internal wikis with the new version
   - Link to the GitHub Release page

3. **Monitoring:**
   - Watch for questions/issues from users
   - Address any problems promptly with a patch release if needed

## Release Checklist

- [ ] All code changes committed and pushed
- [ ] Version numbers updated (if using them)
- [ ] Tests passed (`--selftest` and `--selftest --trn`)
- [ ] Release zip created with `build-release.sh` (lands in `dist/` folder)
- [ ] Verified zip contains no `.ionapi` files
- [ ] Release description prepared
- [ ] Release published on GitHub (upload from `dist/` folder)
- [ ] Users notified with installation/upgrade instructions
- [ ] CHANGELOG.md committed to main branch
- [ ] Note: `dist/` folder is git-ignored and doesn't need to be committed

## Tagging and Versioning

### Version Scheme: Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR** — Breaking changes (e.g., removed tools)
- **MINOR** — New features, backward compatible (e.g., new tools, environments)
- **PATCH** — Bug fixes, backward compatible

**Examples:**
- `v1.0.0` — Initial release
- `v2.0.0` — Multi-environment support (MINOR feature addition)
- `v2.0.1` — Bug fix
- `v2.1.0` — New export format

### GitHub Tags

Create tags on the main branch for each release:
```bash
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0
```

## Cleanup

After successfully publishing a release:

1. **Local cleanup** — Remove the local zip file if desired:
   ```bash
   rm compass-mcp-2.0.0.zip
   ```

2. **Repo maintenance** — No action needed; releases are archived on GitHub

## Future Releases

Repeat this process for each new release. The `build-release.sh` / `build-release.bat` scripts make it easy to build clean, credential-free packages every time.

---

For questions or issues with the release process, refer to:
- [GitHub Releases Documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [CHANGELOG.md](CHANGELOG.md) for what changed
- [UPGRADE_INSTRUCTIONS.md](UPGRADE_INSTRUCTIONS.md) for user guidance
