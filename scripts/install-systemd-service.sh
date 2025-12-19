#!/bin/bash

# ========================================
# Install Systemd Service for Docker Compose
# ========================================
# Script ini akan membuat systemd service untuk
# auto-start docker-compose saat server boot
# ========================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🔧 Installing systemd service for ASMI Backend...${NC}"

# Get current directory
CURRENT_DIR=$(pwd)

# Check if docker-compose.prod.yml exists
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.prod.yml not found!${NC}"
    echo -e "${YELLOW}Run this script from project root directory${NC}"
    exit 1
fi

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/asmi-backend.service"

echo -e "${YELLOW}📝 Creating service file: $SERVICE_FILE${NC}"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=ASMI Backend API Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Service file created!${NC}"

# Reload systemd
echo -e "${YELLOW}🔄 Reloading systemd daemon...${NC}"
sudo systemctl daemon-reload

# Enable service
echo -e "${YELLOW}⚡ Enabling auto-start...${NC}"
sudo systemctl enable asmi-backend.service

echo -e "${GREEN}✅ Service enabled!${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Installation completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Available commands:${NC}"
echo -e "  Start:   ${GREEN}sudo systemctl start asmi-backend${NC}"
echo -e "  Stop:    ${GREEN}sudo systemctl stop asmi-backend${NC}"
echo -e "  Restart: ${GREEN}sudo systemctl restart asmi-backend${NC}"
echo -e "  Status:  ${GREEN}sudo systemctl status asmi-backend${NC}"
echo -e "  Logs:    ${GREEN}journalctl -u asmi-backend -f${NC}"
echo ""
echo -e "${YELLOW}Test auto-start:${NC}"
echo -e "  ${GREEN}sudo reboot${NC} (server akan restart dan app auto-start)"
echo ""
