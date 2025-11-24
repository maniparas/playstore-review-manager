#!/usr/bin/env bash
# ==============================================================================
# Test Runner Script for Google Play Reviews Explorer
# ==============================================================================
# This script runs the test suite with different configurations.
# Usage:
#   ./run_tests.sh               # Run all tests with coverage
#   ./run_tests.sh unit          # Run only unit tests
#   ./run_tests.sh integration   # Run only integration tests
#   ./run_tests.sh fast          # Run tests without coverage (faster)
#   ./run_tests.sh verbose       # Run with verbose output
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found. Please run ./run.sh first.${NC}"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
    pip install -q pytest pytest-cov pytest-asyncio httpx
fi

# Parse command line argument
TEST_MODE="${1:-all}"

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Google Play Reviews Explorer - Test Suite           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

case "$TEST_MODE" in
    unit)
        echo -e "${BLUE}🧪 Running UNIT tests only...${NC}"
        pytest tests/unit/ -v --tb=short
        ;;
    
    integration)
        echo -e "${BLUE}🔗 Running INTEGRATION tests only...${NC}"
        pytest tests/integration/ -v --tb=short
        ;;
    
    fast)
        echo -e "${BLUE}⚡ Running all tests (fast mode, no coverage)...${NC}"
        pytest tests/ -v --tb=short
        ;;
    
    verbose)
        echo -e "${BLUE}📝 Running all tests (verbose mode with coverage)...${NC}"
        pytest tests/ -vv --tb=long --cov=app --cov-report=term-missing --cov-report=html
        ;;
    
    coverage)
        echo -e "${BLUE}📊 Running tests with detailed coverage report...${NC}"
        pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html --cov-branch
        echo ""
        echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    specific)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please specify a test file or pattern${NC}"
            echo -e "${YELLOW}Usage: ./run_tests.sh specific tests/unit/test_schemas.py${NC}"
            exit 1
        fi
        echo -e "${BLUE}🎯 Running specific test: $2${NC}"
        pytest "$2" -v --tb=short
        ;;
    
    all|*)
        echo -e "${BLUE}🚀 Running ALL tests with coverage...${NC}"
        pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-report=html
        ;;
esac

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  ✅ ALL TESTS PASSED! 🎉                     ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                  ❌ SOME TESTS FAILED                        ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo -e "${BLUE}📚 Available test commands:${NC}"
echo -e "  ${YELLOW}./run_tests.sh${NC}               - Run all tests with coverage"
echo -e "  ${YELLOW}./run_tests.sh unit${NC}          - Run only unit tests"
echo -e "  ${YELLOW}./run_tests.sh integration${NC}   - Run only integration tests"
echo -e "  ${YELLOW}./run_tests.sh fast${NC}          - Run without coverage (faster)"
echo -e "  ${YELLOW}./run_tests.sh verbose${NC}       - Run with verbose output"
echo -e "  ${YELLOW}./run_tests.sh coverage${NC}      - Generate detailed coverage report"
echo -e "  ${YELLOW}./run_tests.sh specific <path>${NC} - Run specific test file"
echo ""

exit $EXIT_CODE

