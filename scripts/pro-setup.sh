# Here are production setup commands
# This script sets up the production environment for the project

set -e

echo "🚀 Setting up OSUC Digital Twin Project production environment..."
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
python3 -m venv venv 
echo -e "${GREEN}✅ Virtual environment created${NC}"

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate  

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
echo "📚 Installing production dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Production dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️ requirements.txt not found, skipping dependency installation${NC}"
fi
    echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}⚠️ pre-commit not found, skipping pre-commit hook installation${NC}"
fi  
echo -e "${GREEN}✅ Production environment setup complete!${NC}"