#!/bin/bash
# Create a release zip file (flat structure), excluding credentials and build artifacts
# Usage: bash build-release.sh [version]
# Example: bash build-release.sh 2.0.0
#
# Creates a flat zip structure for easy unzipping directly into existing installation:
#   server.py
#   compass_client.py
#   exporter.py
#   [etc - no root folder]

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

# Create zip with flat structure (no root folder)
echo "Creating zip archive (flat structure)..."
# Use git archive to respect .gitignore, then add it to dist folder
git archive --format=zip --output="$DIST_DIR/$RELEASE_ZIP" HEAD

# Report
echo -e "${GREEN}✓ Release created: $DIST_DIR/$RELEASE_ZIP${NC}"
ls -lh "$DIST_DIR/$RELEASE_ZIP"
echo ""
echo "Next steps:"
echo "  1. Review the zip file: $DIST_DIR/$RELEASE_ZIP"
echo "  2. Create a GitHub Release and upload the zip"
echo "  3. Share the download link with users"
echo ""
echo "Users can extract with:"
echo "  unzip $RELEASE_ZIP -d ~/compass-mcp"
