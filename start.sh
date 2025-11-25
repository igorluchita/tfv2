#!/bin/bash
# Start script for Raspberry Pi

echo "================================================"
echo "  Smart Traffic Light System - Starting..."
echo "================================================"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Start Django server
echo ""
echo "Starting Django web server..."
echo ""
echo "================================================"
echo "  Dashboard will be available at:"
echo "  http://localhost:8000"
echo "  http://<your-raspberry-pi-ip>:8000"
echo "================================================"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python manage.py runserver 0.0.0.0:8000
