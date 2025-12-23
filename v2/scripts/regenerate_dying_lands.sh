#!/usr/bin/env bash
#
# Regenerate Dying Lands output via API for v2 dev environment.
#
# This script calls the /api/bootstrap endpoint to regenerate the dying lands
# output. The server must be running for this to work.
#
# Usage:
#   ./regenerate_dying_lands.sh [options]
#
# Environment variables:
#   HEXY_HOST - API host (default: 127.0.0.1)
#   HEXY_PORT - API port (default: 6660)
#   HEXY_LANGUAGE - Language to use (default: en)
#

set -euo pipefail

# Default configuration
HEXY_HOST="${HEXY_HOST:-127.0.0.1}"
HEXY_PORT="${HEXY_PORT:-6660}"
HEXY_LANGUAGE="${HEXY_LANGUAGE:-en}"
API_URL="http://${HEXY_HOST}:${HEXY_PORT}/api/bootstrap"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1" >&2
}

# Check if curl is available
if ! command -v curl &> /dev/null; then
    error "curl is required but not installed. Please install curl."
    exit 1
fi

# Check if jq is available (optional, for pretty JSON output)
HAS_JQ=false
if command -v jq &> /dev/null; then
    HAS_JQ=true
fi

# Check if server is reachable
info "Checking if server is running at ${API_URL}..."
if ! curl -s -f -o /dev/null "${API_URL}" 2>/dev/null; then
    # Try health endpoint instead
    HEALTH_URL="http://${HEXY_HOST}:${HEXY_PORT}/api/health"
    if ! curl -s -f -o /dev/null "${HEALTH_URL}" 2>/dev/null; then
        error "Server is not reachable at ${HEXY_HOST}:${HEXY_PORT}"
        error "Please ensure the server is running:"
        error "  cd v2 && python -m backend.app"
        exit 1
    fi
fi

success "Server is reachable"

# Set language if specified
if [ -n "${HEXY_LANGUAGE:-}" ]; then
    info "Setting language to ${HEXY_LANGUAGE}..."
    SET_LANG_URL="http://${HEXY_HOST}:${HEXY_PORT}/api/set-language"
    LANG_RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"language\": \"${HEXY_LANGUAGE}\"}" \
        "${SET_LANG_URL}")
    
    if [ "${HAS_JQ}" = true ]; then
        echo "${LANG_RESPONSE}" | jq .
    else
        echo "${LANG_RESPONSE}"
    fi
fi

# Call bootstrap endpoint to regenerate
info "Regenerating dying lands output..."
info "This may take a while..."

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}")
HTTP_CODE=$(echo "${RESPONSE}" | tail -n1)
BODY=$(echo "${RESPONSE}" | sed '$d')

# Check HTTP status code
if [ "${HTTP_CODE}" -eq 200 ]; then
    success "Regeneration completed successfully!"
    echo ""
    if [ "${HAS_JQ}" = true ]; then
        echo "${BODY}" | jq .
    else
        echo "${BODY}"
    fi
    exit 0
else
    error "Regeneration failed with HTTP status ${HTTP_CODE}"
    echo ""
    echo "${BODY}"
    exit 1
fi
