#!/bin/bash
# Quick status check for Customer Success Digital FTE deployment

echo "=========================================="
echo "Customer Success Digital FTE - Status"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Docker
echo "Docker Services:"
if docker ps > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"

    # Check PostgreSQL
    if docker ps | grep -q "customer-success-postgres.*healthy"; then
        echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"

        # Count tables
        TABLE_COUNT=$(docker exec customer-success-postgres psql -U postgres -d customer_success -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | tr -d ' ')
        echo "  Tables: $TABLE_COUNT/7"

        # Count KB articles
        KB_COUNT=$(docker exec customer-success-postgres psql -U postgres -d customer_success -t -c "SELECT COUNT(*) FROM knowledge_base;" 2>/dev/null | tr -d ' ')
        echo "  Knowledge base: $KB_COUNT articles"

        # Count customers
        CUST_COUNT=$(docker exec customer-success-postgres psql -U postgres -d customer_success -t -c "SELECT COUNT(*) FROM customers;" 2>/dev/null | tr -d ' ')
        echo "  Customers: $CUST_COUNT"

        # Count tickets
        TICKET_COUNT=$(docker exec customer-success-postgres psql -U postgres -d customer_success -t -c "SELECT COUNT(*) FROM tickets;" 2>/dev/null | tr -d ' ')
        echo "  Tickets: $TICKET_COUNT"
    else
        echo -e "${RED}✗ PostgreSQL is not healthy${NC}"
    fi

    # Check Kafka
    if docker ps | grep -q "customer-success-kafka"; then
        echo -e "${GREEN}✓ Kafka is running${NC}"

        # Count topics
        TOPIC_COUNT=$(docker exec customer-success-kafka kafka-topics.sh --list --bootstrap-server localhost:9092 2>/dev/null | grep -c "^fte\." || echo "0")
        echo "  Topics: $TOPIC_COUNT"
    else
        echo -e "${RED}✗ Kafka is not running${NC}"
    fi

    # Check Zookeeper
    if docker ps | grep -q "customer-success-zookeeper"; then
        echo -e "${GREEN}✓ Zookeeper is running${NC}"
    else
        echo -e "${RED}✗ Zookeeper is not running${NC}"
    fi
else
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker Desktop"
fi

echo ""
echo "Application Services:"

# Check if FastAPI is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ FastAPI server is running (port 8000)${NC}"

    # Check readiness
    READY=$(curl -s http://localhost:8000/ready | grep -o '"status":"ready"' || echo "")
    if [ -n "$READY" ]; then
        echo -e "${GREEN}✓ FastAPI is ready (DB + Kafka connected)${NC}"
    else
        echo -e "${YELLOW}⚠ FastAPI is running but not ready${NC}"
    fi
else
    echo -e "${YELLOW}⚠ FastAPI server is not running${NC}"
    echo "  Start with: python -m backend.src.main"
fi

# Check if Kafka consumer is running
if ps aux | grep -q "[p]ython.*message_processor.py"; then
    echo -e "${GREEN}✓ Kafka consumer worker is running${NC}"
else
    echo -e "${YELLOW}⚠ Kafka consumer worker is not running${NC}"
    echo "  Start with: python backend/src/workers/message_processor.py"
fi

echo ""
echo "=========================================="
echo "Quick Actions:"
echo "=========================================="
echo "Start services:  ./deploy.sh"
echo "View logs:       docker-compose -f infrastructure/docker-compose.yml logs -f"
echo "Stop services:   docker-compose -f infrastructure/docker-compose.yml down"
echo "Reset database:  docker-compose -f infrastructure/docker-compose.yml down -v"
echo "=========================================="
