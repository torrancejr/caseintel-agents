#!/bin/bash
set -e

echo "Starting application..."

# Ensure packages are installed (in case they're not in runtime)
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "Installing dependencies..."
    python3 -m pip install --no-cache-dir -r requirements.txt
fi

# Start the application
echo "Starting uvicorn server..."
exec python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
