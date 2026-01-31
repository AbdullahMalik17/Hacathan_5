#!/bin/bash
# Kafka topic creation script for Customer Success Digital FTE
# Task: T022 - Create Kafka topic creation script for all topics

set -e  # Exit on error

# Configuration
KAFKA_BOOTSTRAP_SERVERS="${KAFKA_BOOTSTRAP_SERVERS:-localhost:9092}"
PARTITIONS="${KAFKA_PARTITION_COUNT:-12}"
REPLICATION_FACTOR="${KAFKA_REPLICATION_FACTOR:-1}"

echo "========================================="
echo "Kafka Topics Setup"
echo "========================================="
echo "Bootstrap Servers: $KAFKA_BOOTSTRAP_SERVERS"
echo "Partitions: $PARTITIONS"
echo "Replication Factor: $REPLICATION_FACTOR"
echo "========================================="

# Function to create a topic
create_topic() {
    local topic_name=$1
    local description=$2

    echo "Creating topic: $topic_name"
    echo "  Description: $description"

    docker exec customer-success-kafka kafka-topics \
        --create \
        --if-not-exists \
        --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
        --topic "$topic_name" \
        --partitions "$PARTITIONS" \
        --replication-factor "$REPLICATION_FACTOR" \
        --config retention.ms=604800000 \
        --config compression.type=snappy

    if [ $? -eq 0 ]; then
        echo "  ✓ Topic created successfully"
    else
        echo "  ✗ Failed to create topic"
        return 1
    fi
    echo ""
}

# ============================================================================
# Create Topics
# ============================================================================

# Topic: Incoming tickets from all channels
create_topic "fte.tickets.incoming" \
    "All incoming customer messages from email, WhatsApp, and web form"

# Topic: Email channel specific events
create_topic "fte.channels.email.inbound" \
    "Incoming email messages from Gmail webhook"

create_topic "fte.channels.email.outbound" \
    "Outgoing email responses to be sent via Gmail API"

# Topic: WhatsApp channel specific events
create_topic "fte.channels.whatsapp.inbound" \
    "Incoming WhatsApp messages from Twilio webhook"

create_topic "fte.channels.whatsapp.outbound" \
    "Outgoing WhatsApp messages to be sent via Twilio API"

# Topic: Web form channel specific events
create_topic "fte.channels.webform.inbound" \
    "Incoming support form submissions from website"

# Topic: Ticket escalations to human support
create_topic "fte.escalations" \
    "Escalated tickets requiring human support intervention"

# Topic: Dead letter queue for failed message processing
create_topic "fte.dlq" \
    "Dead letter queue for messages that failed processing after retries"

# Topic: Agent responses (for monitoring and analytics)
create_topic "fte.agent.responses" \
    "Agent-generated responses for analytics and quality monitoring"

# Topic: Sentiment analysis results
create_topic "fte.analytics.sentiment" \
    "Customer sentiment scores for analytics"

# ============================================================================
# List all topics
# ============================================================================

echo "========================================="
echo "Verifying topic creation..."
echo "========================================="

docker exec customer-success-kafka kafka-topics \
    --list \
    --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" | grep "^fte\."

echo ""
echo "========================================="
echo "Topic Details"
echo "========================================="

for topic in $(docker exec customer-success-kafka kafka-topics --list --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" | grep "^fte\."); do
    echo "Topic: $topic"
    docker exec customer-success-kafka kafka-topics \
        --describe \
        --bootstrap-server "$KAFKA_BOOTSTRAP_SERVERS" \
        --topic "$topic"
    echo ""
done

echo "========================================="
echo "Kafka topics setup complete!"
echo "========================================="
