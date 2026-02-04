#!/bin/bash
# Test runner script for Customer Success Digital FTE

set -e  # Exit on any error

echo "🔍 Running tests for Customer Success Digital FTE..."

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -r backend/requirements-test.txt

# Run unit tests
echo "🧪 Running unit tests..."
python -m pytest backend/tests/unit -v --cov=backend/src/agent --cov=backend/src/webhooks --cov-report=term-missing

# Run integration tests
echo "⚙️  Running integration tests..."
python -m pytest backend/tests/integration -v

# Run all tests with coverage
echo "📊 Running all tests with coverage..."
python -m pytest backend/tests --cov=backend/src --cov-report=html --cov-report=term-missing

echo "✅ All tests completed!"
echo "📊 Coverage report generated in coverage_report/ directory"