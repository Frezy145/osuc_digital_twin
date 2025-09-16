#!/bin/bash

# Development setup script for OSUC Digital Twin Project
# This script helps new contributors set up their development environment

set -e

echo "🚀 Setting up OSUC Digital Twin Project development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if python3 -c 'import sys; exit(1 if sys.version_info < (3, 8) else 0)'; then
    echo -e "${RED}❌ Python 3.8+ is required. Current version: ${PYTHON_VERSION}${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python ${PYTHON_VERSION} detected${NC}"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📚 Installing development dependencies..."
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
    echo -e "${GREEN}✅ Development dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️ requirements-dev.txt not found, skipping dependency installation${NC}"
fi

# Install pre-commit hooks
echo "🔒 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠️ pre-commit not available, skipping hook installation${NC}"
fi

# Install project in development mode
echo "🔧 Installing project in development mode..."
pip install -e .

# Run initial tests (if they exist)
echo "🧪 Running initial tests..."
if [ -d "tests" ] && command -v pytest &> /dev/null; then
    pytest tests/ -v || echo -e "${YELLOW}⚠️ Some tests failed, but this is expected for a new project${NC}"
else
    echo -e "${YELLOW}⚠️ No tests found or pytest not available${NC}"
fi

# Success message
echo ""
echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: ${YELLOW}source venv/bin/activate${NC}"
echo "2. Read the contributing guide: ${YELLOW}cat CONTRIBUTING.md${NC}"
echo "3. Check out good first issues: ${YELLOW}https://github.com/Frezy145/osuc_digital_twin/labels/good%20first%20issue${NC}"
echo "4. Join the discussion: ${YELLOW}https://github.com/Frezy145/osuc_digital_twin/discussions${NC}"
echo ""
echo "Happy coding! 🚀"