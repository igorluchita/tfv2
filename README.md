# Smart Traffic Light System with Video Detection

An automated smart traffic light system using Raspberry Pi 5, video cameras, and addressable LED strip for intelligent traffic management.

## 🚦 Overview

This project implements a smart traffic light system that automatically detects vehicles using camera-based computer vision and controls traffic lights accordingly. The system ensures optimal traffic flow by only turning lights green when vehicles are detected.

### Key Features

- **Automatic Vehicle Detection**: Uses OpenCV for real-time vehicle detection via video cameras
- **Smart Light Control**: Traffic lights turn green only when vehicles are present
- **Two-Direction Management**: Handles intersection with two traffic directions
- **Safety First**: Both lights are never green simultaneously
- **Web Dashboard**: Real-time monitoring and control interface
- **Event Logging**: Comprehensive activity and event tracking
- **LED Strip Control**: Addressable LED strip simulates traffic lights

## 🔧 Hardware Requirements

- **1x Raspberry Pi 5** (4GB or 8GB RAM recommended)
- **2x USB Cameras** (or Raspberry Pi Camera Modules)
- **1x Addressable LED Strip** (WS2812B/NeoPixel, 6 LEDs minimum)
- **Power Supply** (5V/3A for Raspberry Pi)
- **MicroSD Card** (32GB or larger, Class 10)
- **Jumper Wires** (for LED strip connection)

### Hardware Connections

**LED Strip Connection:**
- LED Strip Data Pin → GPIO 18 (Pin 12)
- LED Strip VCC → 5V (Pin 2 or 4)
- LED Strip GND → GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)

**LED Assignment:**
- LEDs 0-2: Direction 1 (Red, Yellow, Green)
- LEDs 3-5: Direction 2 (Red, Yellow, Green)

**Cameras:**
- Camera 1 → USB Port or CSI connector (Direction 1)
- Camera 2 → USB Port or CSI connector (Direction 2)

## 📦 Software Requirements

- Python 3.9 or higher
- Django 4.2+
- OpenCV (opencv-python)
- rpi-ws281x (for LED control on Raspberry Pi)
- See `requirements.txt` for complete list

## 🚀 Installation Instructions

### Step 1: Prepare Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-venv python3-dev
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y git

# Enable camera interface (if using Pi Camera)
sudo raspi-config
# Navigate to Interface Options → Camera → Enable
```

### Step 2: Clone/Copy Project

```bash
# Navigate to project directory
cd "/path/to/lab refacut"

# Or copy the project files to your Raspberry Pi
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Raspberry Pi
# OR
.\venv\Scripts\activate  # On Windows (for development)
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 5: Configure Django

```bash
# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 6: Configure System Settings

Edit `traffic_system/settings.py` if needed to adjust:

```python
TRAFFIC_CONFIG = {
    'LED_PIN': 18,              # GPIO pin for LED strip
    'LED_COUNT': 6,             # Total LEDs (3 per direction)
    'LED_BRIGHTNESS': 255,      # LED brightness (0-255)
    'CAMERA_DIRECTION_1': 0,    # Camera index for direction 1
    'CAMERA_DIRECTION_2': 1,    # Camera index for direction 2
    'DETECTION_THRESHOLD': 0.3, # Vehicle detection confidence
    'MIN_GREEN_TIME': 5,        # Minimum green light duration (seconds)
    'MAX_GREEN_TIME': 60,       # Maximum green light duration (seconds)
    'CHECK_INTERVAL': 1,        # Check interval (seconds)
}
```

## 🎯 Running the System

### Development Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run Django development server
python manage.py runserver 0.0.0.0:8000
```

### Production Mode (with Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn traffic_system.wsgi:application --bind 0.0.0.0:8000
```

### Access the Dashboard

Open a web browser and navigate to:
- Local: `http://localhost:8000`
- Network: `http://<raspberry-pi-ip>:8000`

### Admin Panel

Access the Django admin panel at:
- `http://localhost:8000/admin`

Use the superuser credentials you created earlier.

## 📱 Using the System

### Dashboard Features

1. **System Controls**
   - Start/Stop button to control the traffic system
   - Real-time system status indicator

2. **Traffic Light Status**
   - Visual representation of both traffic lights
   - Current light state (RED/GREEN)
   - Vehicle count for each direction

3. **Event Log**
   - Real-time event monitoring
   - Light changes and vehicle detections
   - System events and errors

### Traffic Logic

1. **Default State**: Both lights are RED
2. **Vehicle Detection**: When a vehicle is detected in Direction 1:
   - Direction 1 turns GREEN
   - Direction 2 remains RED
3. **Duration Control**:
   - Light stays GREEN while vehicles are present
   - Minimum green time: 5 seconds
   - Maximum green time: 60 seconds
4. **Switching**: When no vehicles in current green direction:
   - Light turns RED
   - System checks other direction
   - If vehicles detected there, that light turns GREEN

## 🔍 Testing Without Hardware

The system includes simulation modes for testing without actual hardware:

1. **Camera Simulation**: If cameras are not detected, system generates random vehicle presence
2. **LED Simulation**: If not running on Raspberry Pi, LED states are logged instead

This allows development and testing on any computer.

## 📊 Project Structure

```
lab refacut/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── db.sqlite3                     # SQLite database (created after migration)
├── traffic_system/                # Django project settings
│   ├── __init__.py
│   ├── settings.py               # Main configuration
│   ├── urls.py                   # URL routing
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
├── traffic_control/               # Main application
│   ├── __init__.py
│   ├── admin.py                  # Admin interface configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Database models
│   ├── views.py                  # Web views and API endpoints
│   ├── urls.py                   # App URL routing
│   ├── signals.py                # Django signals
│   ├── vehicle_detector.py       # Vehicle detection with OpenCV
│   ├── led_controller.py         # LED strip control
│   └── traffic_controller.py     # Main traffic control logic
├── templates/                     # HTML templates
│   └── dashboard.html            # Main dashboard
└── static/                        # Static files (CSS, JS, images)
```

## 🛠️ Troubleshooting

### Camera Issues

```bash
# List available cameras
ls -l /dev/video*

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Error')"
```

### LED Strip Issues

```bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER

# Test LED strip
sudo python3 -c "from rpi_ws281x import PixelStrip, Color; strip = PixelStrip(6, 18); strip.begin(); print('LED OK')"
```

### Port Already in Use

```bash
# Kill process using port 8000
sudo lsof -t -i:8000 | xargs kill -9

# Or use different port
python manage.py runserver 0.0.0.0:8080
```

### Permission Denied (GPIO/Camera)

```bash
# Add user to required groups
sudo usermod -a -G video,gpio $USER

# Reboot
sudo reboot
```

## 🔐 Security Notes

- Change `SECRET_KEY` in `settings.py` for production
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` appropriately
- Use HTTPS in production environment
- Secure camera feeds if accessible over network

## 📝 Logging

Logs are stored in:
- **Application Log**: `traffic_system.log`
- **Django Console**: Standard output

View logs in real-time:
```bash
tail -f traffic_system.log
```

## 🎓 System Architecture

### Components

1. **Vehicle Detector** (`vehicle_detector.py`)
   - Captures video from cameras
   - Detects vehicles using OpenCV
   - Returns vehicle count

2. **LED Controller** (`led_controller.py`)
   - Controls addressable LED strip
   - Manages light states (RED/GREEN/YELLOW)
   - Simulates traffic lights

3. **Traffic Controller** (`traffic_controller.py`)
   - Main coordination logic
   - Manages traffic flow rules
   - Ensures safety (no simultaneous greens)

4. **Django Web Interface**
   - Real-time dashboard
   - API endpoints for control
   - Event logging and history

## 🔄 Future Enhancements

- [ ] Advanced vehicle detection (YOLO, MobileNet SSD)
- [ ] Traffic density analysis
- [ ] Historical traffic patterns
- [ ] Mobile app integration
- [ ] Multiple intersection support
- [ ] Emergency vehicle priority
- [ ] Pedestrian crossing detection

## 📄 License

This project is developed for educational purposes.

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs (`traffic_system.log`)
3. Ensure all hardware connections are correct
4. Verify all dependencies are installed

---

**Developed for Raspberry Pi 5 - Smart Traffic Management System**
