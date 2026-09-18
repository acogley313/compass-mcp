# GitHub Release Instructions

**Process guide for creating and publishing releases on GitHub.**

Version content (what changed, features, fixes) is documented in `CHANGELOG.md`. This guide covers the release process only.

## Before Releasing

1. **Verify CHANGELOG.md is up to date** with the new version
2. **Ensure all changes are committed and pushed**
   ```bash
   git status
   git push origin main
   ```
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

## Publishing the Release

**Option A: Using GitHub CLI (recommended)**

```bash
gh release create v2.0.0 \
  -t "Compass MCP 2.0.0" \
  -F CHANGELOG.md \
  dist/compass-mcp-2.0.0.zip
```

Add `--draft` to create a draft first, then publish from GitHub's web interface.

**Option B: GitHub Web Interface**

1. Go to your GitHub repository
2. Click **Releases** → **Draft a new release**
3. Fill in:
   - **Tag version:** `v2.0.0`
   - **Release title:** `Compass MCP 2.0.0`
   - **Description:** Copy the version section from `CHANGELOG.md`, or use this template:
     ```markdown
     **Installation:** New users should follow README.md. Existing users should review UPGRADE_INSTRUCTIONS.md.
     
     [Paste the relevant section from CHANGELOG.md here]
     ```
   - **Binaries:** Drag `dist/compass-mcp-2.0.0.zip` into the upload area
4. Click **Publish release**

## After Publishing

- Post the release link in Slack/email
- Direct users to `UPGRADE_INSTRUCTIONS.md` for existing installs
- Point new users to the README.md Quick Start
- Update any internal wikis with the new version

## Release Checklist

- [ ] CHANGELOG.md updated with new version
- [ ] Code committed and pushed to main
- [ ] Tests pass (`--selftest` and `--selftest --trn`)
- [ ] Release zip created with `build-release.sh`
- [ ] Zip contains no `.ionapi` files
- [ ] Release published on GitHub
- [ ] Users notified

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

## Reference

- **What changed:** See [CHANGELOG.md](CHANGELOG.md)
- **User upgrade guide:** See [UPGRADE_INSTRUCTIONS.md](UPGRADE_INSTRUCTIONS.md)
- **GitHub releases docs:** https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
