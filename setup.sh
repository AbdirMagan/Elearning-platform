#!/bin/bash

# E-Learning Platform Setup Script
# This script automates the setup process for the e-learning platform

set -e  # Exit on error

echo "========================================="
echo "E-Learning Platform Setup"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate || . venv/Scripts/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Requirements installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env file with your configuration${NC}"
else
    echo -e "${GREEN}.env file already exists${NC}"
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py makemigrations
python manage.py migrate
echo -e "${GREEN}✓ Migrations completed${NC}"

# Create superuser
echo -e "${YELLOW}Creating superuser...${NC}"
echo "Please enter superuser credentials:"
python manage.py createsuperuser

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"

# Create media directories
echo -e "${YELLOW}Creating media directories...${NC}"
mkdir -p media/courses/thumbnails
mkdir -p media/courses/videos
mkdir -p media/courses/materials
mkdir -p media/courses/promo_videos
mkdir -p media/profile_pics
echo -e "${GREEN}✓ Media directories created${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your WaafiPay credentials"
echo "2. Run: python manage.py runserver"
echo "3. Visit: http://127.0.0.1:8000"
echo "4. Admin panel: http://127.0.0.1:8000/admin"
echo ""
echo "For production deployment, see README.md"
echo ""
