#!/bin/bash
# Customer Success Digital FTE - Deployment Script
# This script sets up the complete Phase 3 environment

set -e  # Exit on error

echo "=========================================="
echo "Customer Success Digital FTE - Deployment"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# Step 1: Start infrastructure
echo ""
echo "Step 1: Starting infrastructure (PostgreSQL + Kafka)..."
cd infrastructure
docker compose up -d

echo "Waiting for services to be healthy (30 seconds)..."
sleep 30

# Verify services are running
if docker ps | grep -q "customer-success-postgres"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL failed to start${NC}"
    exit 1
fi

if docker ps | grep -q "customer-success-kafka"; then
    echo -e "${GREEN}✓ Kafka is running${NC}"
else
    echo -e "${RED}✗ Kafka failed to start${NC}"
    exit 1
fi

cd ..

# Step 2: Check database schema
echo ""
echo "Step 2: Verifying database schema..."
TABLE_COUNT=$(docker exec customer-success-postgres psql -U postgres -d customer_success -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")
TABLE_COUNT=$(echo $TABLE_COUNT | tr -d ' ')

if [ "$TABLE_COUNT" -eq "7" ]; then
    echo -e "${GREEN}✓ Database schema loaded (7 tables)${NC}"
else
    echo -e "${YELLOW}⚠ Loading database schema...${NC}"
    docker exec -i customer-success-postgres psql -U postgres -d customer_success < database/schema.sql
    echo -e "${GREEN}✓ Database schema created${NC}"
fi

# Step 3: Seed knowledge base
echo ""
echo "Step 3: Seeding knowledge base..."

# Check if .env exists and has OpenAI key
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠ Creating .env file from template${NC}"
    cp backend/.env.example backend/.env
    echo -e "${RED}⚠ IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY${NC}"
    echo "Then re-run this script."
    exit 1
fi

# Check if knowledge base is already seeded
KB_COUNT=$(docker exec customer-success-postgres psql -U postgres -d customer_success -t -c "SELECT COUNT(*) FROM knowledge_base;" 2>/dev/null || echo "0")
KB_COUNT=$(echo $KB_COUNT | tr -d ' ')
KB_COUNT=${KB_COUNT:-0}

if [ "$KB_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✓ Knowledge base already seeded ($KB_COUNT articles)${NC}"
else
    echo "Running seed script..."
    backend/venv/bin/python scripts/seed_knowledge_base.py || {
        echo -e "${RED}✗ Knowledge base seeding failed${NC}"
        echo "Make sure OPENAI_API_KEY is set in backend/.env"
        exit 1
    }
    echo -e "${GREEN}✓ Knowledge base seeded${NC}"
fi

# Step 4: Setup Kafka topics
echo ""
echo "Step 4: Setting up Kafka topics..."

# Check if topics exist
TOPIC_COUNT=$(docker exec customer-success-kafka kafka-topics.sh --list --bootstrap-server localhost:9092 2>/dev/null | grep -c "^fte\." || echo "0")

if [ "$TOPIC_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✓ Kafka topics already created ($TOPIC_COUNT topics)${NC}"
else
    echo "Creating topics..."
    bash scripts/setup_kafka_topics.sh || {
        echo -e "${RED}✗ Kafka topic creation failed${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Kafka topics created${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo -e "${GREEN}✓ PostgreSQL running and schema loaded${NC}"
echo -e "${GREEN}✓ Kafka running with topics configured${NC}"
echo -e "${GREEN}✓ Knowledge base seeded${NC}"
echo ""
echo "Next steps:"
echo "1. Start FastAPI server:"
echo "   backend/venv/bin/python -m backend.src.main"
echo ""
echo "2. Start Kafka consumer (in another terminal):"
echo "   backend/venv/bin/python backend/src/workers/message_processor.py"
echo ""
echo "3. Test the deployment:"
echo "   curl http://localhost:8000/health"
echo ""
echo "See DEPLOYMENT_GUIDE.md for full testing instructions."
echo "=========================================="
