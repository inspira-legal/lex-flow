#!/bin/bash
# Google Cloud Pub/Sub Emulator Setup Script
#
# This script sets up and starts the Pub/Sub emulator for local testing.
#
# Prerequisites:
# - Google Cloud SDK installed (gcloud)
# - Or Docker installed
#
# Usage:
#   ./setup.sh         # Start emulator using gcloud
#   ./setup.sh docker  # Start emulator using Docker

set -e

EMULATOR_HOST="localhost:8085"
PROJECT_ID="test-project"
TOPIC_ID="test-topic"
SUBSCRIPTION_ID="test-subscription"

echo "=== Pub/Sub Emulator Setup ==="
echo ""

# Check if using Docker mode
if [ "$1" = "docker" ]; then
    echo "Starting Pub/Sub emulator with Docker..."
    echo ""

    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed."
        echo "Install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Stop any existing emulator container
    docker stop pubsub-emulator 2>/dev/null || true
    docker rm pubsub-emulator 2>/dev/null || true

    # Start the emulator
    echo "Starting emulator container..."
    docker run -d \
        --name pubsub-emulator \
        -p 8085:8085 \
        gcr.io/google.com/cloudsdktool/cloud-sdk:emulators \
        gcloud beta emulators pubsub start \
        --host-port=0.0.0.0:8085 \
        --project=$PROJECT_ID

    echo "Waiting for emulator to start..."
    until curl -s -o /dev/null "http://$EMULATOR_HOST"; do
        echo -n "."
        sleep 1
    done
    echo " Emulator is up!"

else
    echo "Starting Pub/Sub emulator with gcloud..."
    echo ""

    # Check if gcloud is available
    if ! command -v gcloud &> /dev/null; then
        echo "Error: gcloud is not installed."
        echo ""
        echo "Install options:"
        echo "  1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        echo "  2. Use Docker mode: ./setup.sh docker"
        exit 1
    fi

    # Check if emulator component is installed
    if ! gcloud components list 2>/dev/null | grep -q "pubsub-emulator.*Installed"; then
        echo "Installing Pub/Sub emulator component..."
        gcloud components install pubsub-emulator
    fi

    echo "Starting emulator (this will run in foreground)..."
    echo "Press Ctrl+C to stop"
    echo ""
    echo "In another terminal, run:"
    echo "  export PUBSUB_EMULATOR_HOST=$EMULATOR_HOST"
    echo "  ./create_resources.sh"
    echo ""

    # Start the emulator
    gcloud beta emulators pubsub start --host-port=$EMULATOR_HOST --project=$PROJECT_ID
fi

echo ""
echo "=== Emulator Started ==="
echo ""
echo "Emulator host: $EMULATOR_HOST"
echo "Project ID: $PROJECT_ID"
echo ""
echo "Set environment variable:"
echo "  export PUBSUB_EMULATOR_HOST=$EMULATOR_HOST"
echo ""
echo "Then create topic and subscription:"
echo "  ./create_resources.sh"
