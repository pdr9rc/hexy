#!/bin/bash

echo "🗺️ Starting Hexy ASCII Map Viewer..."
echo "=================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python..."
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
else
    echo "⚠️  No requirements.txt found. Installing common dependencies..."
    pip install -q flask markdown
fi

# Set Python path to include src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

echo "✅ Starting Flask server..."
echo "🌐 Web interface will be available at: http://127.0.0.1:5000"
echo "📱 API endpoints available at: http://127.0.0.1:5000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Launch the ASCII map viewer
cd src
python3 ascii_map_viewer.py