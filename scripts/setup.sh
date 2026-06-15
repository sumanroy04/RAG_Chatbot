#!/bin/bash
# setup.sh - Initial project setup scripts

echo "🚀 Setting up Mental Health Chatbot..."

# Create Python virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate venv and install requirements
echo "📥 Installing backend packages..."
source .venv/bin/activate || source .venv/Scripts/activate
pip install -r requirements/dev.txt

# Install frontend dependencies
echo "📦 Installing frontend NPM packages..."
cd frontend
npm install
cd ..

echo "✅ Setup complete! Use .\run.ps1 to start."
