#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="electrum-plugins-website"
IMAGE_NAME="electrum-plugins-website"
PORT=80

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if container is already running
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container '${CONTAINER_NAME}' is already running."
    exit 0
fi

# Remove stopped container with the same name if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Removing stopped container '${CONTAINER_NAME}'..."
    docker rm "${CONTAINER_NAME}"
fi

# Copy site files into build context
echo "Preparing site files..."
rm -rf "$SCRIPT_DIR/site"
mkdir -p "$SCRIPT_DIR/site"
cp -r "$REPO_DIR/index.html" \
      "$REPO_DIR/plugins.html" \
      "$REPO_DIR/developers.html" \
      "$REPO_DIR/css" \
      "$REPO_DIR/assets" \
      "$SCRIPT_DIR/site/"

# Build the image
echo "Building image '${IMAGE_NAME}'..."
docker build \
    -f "$SCRIPT_DIR/Dockerfile" \
    -t "${IMAGE_NAME}" \
    "$SCRIPT_DIR"

# Clean up copied site files
rm -rf "$SCRIPT_DIR/site"

# Run container
echo "Starting container '${CONTAINER_NAME}' on port ${PORT}..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    --restart unless-stopped \
    -p "${PORT}:${PORT}" \
    "${IMAGE_NAME}"

echo "Container '${CONTAINER_NAME}' is running on port ${PORT}."
