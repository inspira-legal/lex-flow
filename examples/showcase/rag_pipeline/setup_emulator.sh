#!/bin/bash
# Create Pub/Sub resources for the RAG pipeline in the local emulator
#
# Prerequisites:
# - docker-compose up -d (starts Qdrant + Pub/Sub emulator)
# - PUBSUB_EMULATOR_HOST environment variable set
#
# Usage:
#   export PUBSUB_EMULATOR_HOST=localhost:8085
#   ./setup_emulator.sh

set -e

EMULATOR_HOST="${PUBSUB_EMULATOR_HOST:-localhost:8085}"
PROJECT_ID="inspira-development"
TOPIC_ID="document-uploaded"
SUBSCRIPTION_ID="document-uploaded-sub"

echo "=== RAG Pipeline Pub/Sub Setup ==="
echo ""
echo "Emulator:     $EMULATOR_HOST"
echo "Project:      $PROJECT_ID"
echo "Topic:        $TOPIC_ID"
echo "Subscription: $SUBSCRIPTION_ID"
echo ""

# Wait for emulator to be ready
echo "Waiting for emulator..."
until curl -s -o /dev/null "http://$EMULATOR_HOST"; do
    echo -n "."
    sleep 1
done
echo " Ready!"
echo ""

# Create topic
echo "Creating topic: $TOPIC_ID"
curl -s -X PUT "http://$EMULATOR_HOST/v1/projects/$PROJECT_ID/topics/$TOPIC_ID" \
    -H "Content-Type: application/json" \
    -d '{}' || echo "(may already exist)"
echo ""

# Create subscription
echo "Creating subscription: $SUBSCRIPTION_ID"
curl -s -X PUT "http://$EMULATOR_HOST/v1/projects/$PROJECT_ID/subscriptions/$SUBSCRIPTION_ID" \
    -H "Content-Type: application/json" \
    -d "{
        \"topic\": \"projects/$PROJECT_ID/topics/$TOPIC_ID\",
        \"ackDeadlineSeconds\": 120
    }" || echo "(may already exist)"
echo ""

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Run the consumer:"
echo "  export PUBSUB_EMULATOR_HOST=$EMULATOR_HOST"
echo "  lexflow examples/showcase/vault/ingest_book_consumer.yaml \\"
echo "    --input project_id=$PROJECT_ID \\"
echo "    --input subscription_name=$SUBSCRIPTION_ID \\"
echo "    --input api_token=YOUR_JWT_TOKEN"
echo ""
echo "Or run the RAG pipeline:"
echo "  lexflow examples/showcase/rag_pipeline/pubsub_ingest_pipeline.yaml \\"
echo "    --input project=$PROJECT_ID \\"
echo "    --input subscription_id=$SUBSCRIPTION_ID"
