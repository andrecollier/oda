#!/bin/bash

# Oda Meal Planner Setup Script

set -e

echo "🍽️  Oda Meal Planner Setup"
echo "=========================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"
echo ""

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Activated"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -e .
echo "✓ Dependencies installed"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
echo "✓ Playwright installed"
echo ""

# Create data directory
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
    echo "✓ Data directory created"
else
    echo "✓ Data directory exists"
fi
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "Please create .env file with your credentials:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env with your API keys"
    echo ""
    echo "Required:"
    echo "  - KASSAL_API_KEY (from https://kassal.app/)"
    echo "  - ODA_EMAIL"
    echo "  - ODA_PASSWORD"
    echo ""
else
    echo "✓ .env file exists"
    echo ""
fi

echo "=========================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your credentials (if not done)"
echo "  2. Activate venv: source .venv/bin/activate"
echo "  3. Start server: python server.py"
echo "  4. Use with Claude Code!"
echo ""
