#!/bin/bash
# Create Pub/Sub resources in the emulator
#
# This script creates a topic and subscription in the local emulator.
#
# Prerequisites:
# - Emulator running (./setup.sh or ./setup.sh docker)
# - PUBSUB_EMULATOR_HOST environment variable set
#
# Usage:
#   export PUBSUB_EMULATOR_HOST=localhost:8085
#   ./create_resources.sh

set -e

EMULATOR_HOST="${PUBSUB_EMULATOR_HOST:-localhost:8085}"
PROJECT_ID="test-project"
TOPIC_ID="test-topic"
SUBSCRIPTION_ID="test-subscription"

echo "=== Creating Pub/Sub Resources ==="
echo ""
echo "Emulator: $EMULATOR_HOST"
echo "Project: $PROJECT_ID"
echo ""

# Create topic
echo "Creating topic: $TOPIC_ID"
curl -s -X PUT "http://$EMULATOR_HOST/v1/projects/$PROJECT_ID/topics/$TOPIC_ID" \
    -H "Content-Type: application/json" \
    -d '{}' || echo "Topic may already exist"

echo ""

# Create subscription
echo "Creating subscription: $SUBSCRIPTION_ID"
curl -s -X PUT "http://$EMULATOR_HOST/v1/projects/$PROJECT_ID/subscriptions/$SUBSCRIPTION_ID" \
    -H "Content-Type: application/json" \
    -d "{
        \"topic\": \"projects/$PROJECT_ID/topics/$TOPIC_ID\",
        \"ackDeadlineSeconds\": 60
    }" || echo "Subscription may already exist"

echo ""
echo ""
echo "=== Resources Created ==="
echo ""
echo "Topic: projects/$PROJECT_ID/topics/$TOPIC_ID"
echo "Subscription: projects/$PROJECT_ID/subscriptions/$SUBSCRIPTION_ID"
echo ""
echo "You can now run the example workflows with:"
echo "  export PUBSUB_EMULATOR_HOST=$EMULATOR_HOST"
echo "  lexflow examples/integrations/pubsub/emulator/publisher.yaml"
echo "  lexflow examples/integrations/pubsub/emulator/streaming_consumer.yaml"
