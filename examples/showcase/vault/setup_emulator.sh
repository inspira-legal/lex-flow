#!/bin/bash
# Create Pub/Sub resources for Vault ingestion pipeline
#
# Creates the topic and subscription used by the book ingestion consumer.
#
# Prerequisites:
# - Emulator running (cd examples/integrations/pubsub/emulator && ./setup.sh docker)
# - PUBSUB_EMULATOR_HOST environment variable set
#
# Usage:
#   export PUBSUB_EMULATOR_HOST=localhost:8085
#   ./examples/showcase/vault/setup_emulator.sh

set -e

EMULATOR_HOST="${PUBSUB_EMULATOR_HOST:-localhost:8085}"
PROJECT_ID="test-project"
TOPIC_ID="vault-ingest"
SUBSCRIPTION_ID="vault-ingest-sub"

echo "=== Creating Vault Pub/Sub Resources ==="
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
echo "Run the consumer:"
echo "  PUBSUB_EMULATOR_HOST=$EMULATOR_HOST lexflow examples/showcase/vault/ingest_book_consumer.yaml"
echo ""
echo "Publish a test message:"
echo "  PUBSUB_EMULATOR_HOST=$EMULATOR_HOST lexflow examples/showcase/vault/publish_book.yaml \\"
echo "    --input bucket=mvp-personal-vault \\"
echo "    --input objeto=solar_system.pdf \\"
echo "    --input livro_id=test-001 \\"
echo "    --input projeto_gcp=inspira-development \\"
echo "    --input workspace_id=ws-abc123 \\"
echo "    --input folder_id=folder-xyz789"
