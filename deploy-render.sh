#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}  Censorly Render Deployment Helper Script   ${NC}"
echo -e "${GREEN}=============================================${NC}"

# Check if render-cli is installed
if ! command -v render &> /dev/null; then
    echo -e "${YELLOW}Render CLI not found. Installing...${NC}"
    brew install render-cli || {
        echo -e "${RED}Failed to install render-cli. Please install it manually:${NC}"
        echo "brew install render-cli"
        exit 1
    }
fi

# Check for required environment variables
if [ -z "$RENDER_API_KEY" ]; then
    echo -e "${YELLOW}RENDER_API_KEY environment variable not set.${NC}"
    echo -e "${YELLOW}Please set it with:${NC}"
    echo "export RENDER_API_KEY=your_render_api_key"
    exit 1
fi

# Validate render.yaml file
echo -e "${GREEN}Validating render.yaml file...${NC}"
if ! render validate --file render.yaml; then
    echo -e "${RED}render.yaml validation failed. Please fix the issues and try again.${NC}"
    exit 1
fi

# Confirm deployment
echo
echo -e "${YELLOW}Which service would you like to deploy?${NC}"
echo "1) Main API service"
echo "2) Debug API service"
echo "3) Both services"
echo "4) Cancel"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}Deploying main API service...${NC}"
        render deploy --file render.yaml --service censorly-api
        ;;
    2)
        echo -e "${GREEN}Deploying debug API service...${NC}"
        render deploy --file render.yaml --service censorly-debug
        ;;
    3)
        echo -e "${GREEN}Deploying all services...${NC}"
        render deploy --file render.yaml
        ;;
    4)
        echo -e "${YELLOW}Deployment cancelled.${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo
echo -e "${GREEN}Deployment initiated. Check the Render dashboard for progress.${NC}"
echo "https://dashboard.render.com/"
