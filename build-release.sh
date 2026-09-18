#!/bin/bash
# Create a release zip file, excluding credentials and build artifacts
# Usage: bash release.sh [version]
# Example: bash release.sh 2.0.0

set -e

VERSION="${1:-development}"
RELEASE_NAME="compass-mcp-${VERSION}"
RELEASE_ZIP="${RELEASE_NAME}.zip"
DIST_DIR="dist"

# Create dist folder if it doesn't exist
mkdir -p "$DIST_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Building release: $RELEASE_NAME${NC}"

# Create a temporary directory for the release
TEMP_DIR=$(mktemp -d)
RELEASE_DIR="${TEMP_DIR}/${RELEASE_NAME}"
mkdir -p "$RELEASE_DIR"

# Copy files, excluding credentials and build artifacts
echo "Copying files..."
rsync -a \
  --exclude='.git' \
  --exclude='.gitignore' \
  --exclude='.venv' \
  --exclude='*.ionapi' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.DS_Store' \
  --exclude='*.egg-info' \
  --exclude='dist/' \
  --exclude='dist' \
  --exclude='build' \
  --exclude='.idea' \
  --exclude='*.iml' \
  --exclude='*.zip' \
  --exclude='.claude/settings.local.json' \
  . "$RELEASE_DIR/"

# Create the zip file
echo "Creating zip archive..."
ORIGINAL_DIR=$(pwd)
cd "$TEMP_DIR"
zip -r -q "$RELEASE_ZIP" "$RELEASE_NAME"

# Move to dist folder
mv "$TEMP_DIR/$RELEASE_ZIP" "$ORIGINAL_DIR/$DIST_DIR/$RELEASE_ZIP"

# Cleanup
rm -rf "$TEMP_DIR"

# Report
echo -e "${GREEN}✓ Release created: $DIST_DIR/$RELEASE_ZIP${NC}"
ls -lh "$ORIGINAL_DIR/$DIST_DIR/$RELEASE_ZIP"
echo ""
echo "Next steps:"
echo "  1. Review the zip file: $DIST_DIR/$RELEASE_ZIP"
echo "  2. Create a GitHub Release and upload the zip"
echo "  3. Share the download link with users"
