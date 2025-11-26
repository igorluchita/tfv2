#!/bin/bash
# Raspberry Pi Setup Script
# Run this script on your Raspberry Pi to set up the traffic light system

echo "================================================"
echo "  Smart Traffic Light System - Raspberry Pi Setup"
echo "================================================"
echo ""

# Update system
echo "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Update package list
echo ""
echo "Step 2a: Updating package list..."
sudo apt update

# Install system dependencies
echo ""
echo "Step 2b: Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y git
sudo apt install -y v4l-utils

# Install OpenCV dependencies
echo ""
echo "Step 2c: Installing OpenCV..."
sudo apt install -y libopencv-dev python3-opencv

# Install libcamera for Camera Module 3
echo ""
echo "Step 2d: Installing libcamera tools for Camera Module 3..."
sudo apt install -y libcamera-apps libcamera-dev

# Enable camera and GPIO (if not already enabled)
echo ""
echo "Step 3: Checking Raspberry Pi Camera Module 3..."
echo "Note: Camera modules should be enabled in raspi-config"
echo ""
echo "Detecting cameras..."
if command -v libcamera-hello &> /dev/null; then
    echo "Using libcamera:"
    libcamera-hello --list-cameras 2>/dev/null || echo "No cameras detected via libcamera"
else
    echo "libcamera-apps not installed yet, will check V4L2..."
fi
echo ""
echo "V4L2 devices:"
if command -v v4l2-ctl &> /dev/null; then
    v4l2-ctl --list-devices 2>/dev/null || echo "No V4L2 devices found"
else
    echo "v4l-utils not installed yet"
fi
echo ""
echo "Video devices:"
ls -l /dev/video* 2>/dev/null || echo "No video devices found - cameras may need to be enabled in raspi-config"

# Create virtual environment
echo ""
echo "Step 4: Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo ""
echo "Step 5: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-rpi.txt

# Run database migrations
echo ""
echo "Step 6: Setting up database..."
python manage.py migrate

# Create superuser prompt
echo ""
echo "Step 7: Create admin user (optional - press Ctrl+C to skip)"
python manage.py createsuperuser

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "================================================"
echo "  Hardware Setup Instructions"
echo "================================================"
echo ""
echo "1. Enable Camera Modules:"
echo "   sudo raspi-config"
echo "   -> Interface Options -> Camera -> Enable"
echo ""
echo "2. Connect Hardware:"
echo "   - Camera Module 1 -> CSI Port 1 (or CAM0)"
echo "   - Camera Module 2 -> CSI Port 2 (or CAM1)"
echo "   - LED Strip Data -> GPIO 18 (Pin 12)"
echo "   - LED Strip VCC -> 5V (Pin 2 or 4)"
echo "   - LED Strip GND -> Ground (Pin 6)"
echo ""
echo "3. Reboot after enabling cameras:"
echo "   sudo reboot"
echo ""
echo "4. Test cameras:"
echo "   v4l2-ctl --list-devices"
echo "   libcamera-hello --list-cameras"
echo ""
echo "5. Start the system:"
echo "   sudo venv/bin/python manage.py runserver 0.0.0.0:8000"
echo ""
echo "Access dashboard at: http://<raspberry-pi-ip>:8000"
echo ""
