#!/bin/bash
# Azure Deployment Helper Script for Customer Success Digital FTE

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Azure Deployment Helper ===${NC}"
echo "This script will help you deploy the Backend to Azure Container Apps."

# Check if az CLI is installed
if ! command -v az &> /dev/null
then
    echo -e "${RED}Error: az CLI not found. Please install it first.${NC}"
    exit 1
fi

# Configuration - Change these or provide as env vars
RESOURCE_GROUP=${RESOURCE_GROUP:-"fte-group"}
LOCATION=${LOCATION:-"eastus"}
ENVIRONMENT_NAME=${ENVIRONMENT_NAME:-"fte-env"}
API_APP_NAME=${API_APP_NAME:-"fte-api"}
WORKER_APP_NAME=${WORKER_APP_NAME:-"fte-worker"}

echo -e "${YELLOW}Step 1: Resource Group and Environment${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION
az containerapp env create --name $ENVIRONMENT_NAME --resource-group $RESOURCE_GROUP --location $LOCATION

echo -e "${YELLOW}Step 2: Setup Azure Event Hubs (Kafka)${NC}"
NS_NAME="fte-kafka-${RANDOM}"
az eventhubs namespace create --name $NS_NAME --resource-group $RESOURCE_GROUP --location $LOCATION --sku Standard
az eventhubs eventhub create --name "fte.tickets.incoming" --resource-group $RESOURCE_GROUP --namespace-name $NS_NAME
CONNECTION_STRING=$(az eventhubs namespace authorization-rule keys list --name RootManageSharedAccessKey --resource-group $RESOURCE_GROUP --namespace-name $NS_NAME --query primaryConnectionString -o tsv)

echo -e "${YELLOW}Step 3: Deploy Backend API${NC}"
echo "Make sure you have your .env file ready or provide variables when prompted."

# Note: Using 'az containerapp up' is the fastest way to build and deploy from source
az containerapp up \
  --name $API_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --source ./backend \
  --ingress external \
  --target-port 8000

# Get the image name used by 'up' to reuse for the worker
IMAGE_NAME=$(az containerapp show --name $API_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.template.containers[0].image" -o tsv)

echo -e "${YELLOW}Step 3: Deploy Backend Worker${NC}"
# Deploy the worker using the same image but different command
az containerapp create \
  --name $WORKER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $IMAGE_NAME \
  --command "python" "-m" "src.workers.message_processor"

echo -e "${GREEN}=== Deployment Commands Initiated ===${NC}"
echo "Now go to the Azure Portal to configure your Environment Variables (Secrets) for:"
echo "- DATABASE_URL"
echo "- KAFKA_BOOTSTRAP_SERVERS=$NS_NAME.servicebus.windows.net:9093"
echo "- KAFKA_SASL_USERNAME=\$ConnectionString"
echo "- KAFKA_SASL_PASSWORD=$CONNECTION_STRING"
echo "- OPENAI_API_KEY"
echo ""
echo "Your API is available at:"
az containerapp show --name $API_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv