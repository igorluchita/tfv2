# 🚦 Quick Start Guide - Smart Traffic Light System

## ✅ Setup Complete!

Your Smart Traffic Light System project has been successfully created with all necessary files and dependencies installed.

## 📁 Project Structure

```
lab refacut/
├── venv/                          ✓ Virtual environment (created)
├── manage.py                      ✓ Django management script
├── requirements.txt               ✓ Core dependencies
├── requirements-windows.txt       ✓ Windows development
├── requirements-rpi.txt           ✓ Raspberry Pi deployment
├── traffic_system/                ✓ Django project settings
├── traffic_control/               ✓ Main application
├── templates/                     ✓ HTML templates
├── README.md                      ✓ Full documentation
└── start.ps1 / start.sh          ✓ Startup scripts

Database: ✓ Migrated and ready
```

## 🚀 How to Start the System

### On Windows (Current System):

```powershell
# Option 1: Use the startup script
.\start.ps1

# Option 2: Manual start
.\venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

### On Raspberry Pi:

```bash
# Make the script executable (first time only)
chmod +x start.sh

# Start the system
./start.sh
```

## 🌐 Access the Dashboard

After starting the server, open your web browser:

- **Local access**: http://localhost:8000
- **Network access**: http://<your-ip>:8000

## 🎮 Using the Dashboard

1. **Start System** - Click to activate vehicle detection and traffic control
2. **Stop System** - Click to deactivate and set all lights to RED
3. **Monitor Status** - Watch real-time updates of:
   - Traffic light states (RED/GREEN)
   - Vehicle counts in each direction
   - Event log

## 🔧 For Raspberry Pi Deployment

When deploying to Raspberry Pi, follow these additional steps:

### 1. Install Raspberry Pi Dependencies

```bash
# On Raspberry Pi, install LED library dependencies
pip install -r requirements-rpi.txt
```

### 2. Hardware Setup

Connect the LED strip to GPIO 18 (Physical Pin 12):
- **Data** → GPIO 18
- **VCC** → 5V
- **GND** → Ground

Connect USB cameras to available USB ports.

### 3. Verify Hardware

```bash
# Check cameras
ls -l /dev/video*

# Test LED strip (requires sudo)
sudo python3 -c "from rpi_ws281x import PixelStrip; print('LED library OK')"
```

### 4. Run with Proper Permissions

```bash
# LED control requires root permissions on Raspberry Pi
sudo venv/bin/python manage.py runserver 0.0.0.0:8000
```

## 📋 Admin Panel

Create a superuser to access the admin panel:

```bash
# Activate venv first
python manage.py createsuperuser

# Then access: http://localhost:8000/admin
```

## 🧪 Testing Without Hardware

The system runs in **simulation mode** when hardware is not detected:

- ✅ Works on Windows for development
- ✅ Simulates vehicle detection (random)
- ✅ Logs LED states instead of hardware control
- ✅ Full dashboard functionality

## 📊 System Configuration

Edit `traffic_system/settings.py` to configure:

```python
TRAFFIC_CONFIG = {
    'LED_PIN': 18,              # GPIO pin
    'LED_COUNT': 6,             # Total LEDs
    'CAMERA_DIRECTION_1': 0,    # Camera index
    'CAMERA_DIRECTION_2': 1,    # Camera index
    'MIN_GREEN_TIME': 5,        # Seconds
    'MAX_GREEN_TIME': 60,       # Seconds
    'CHECK_INTERVAL': 1,        # Seconds
}
```

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Use different port
python manage.py runserver 8080
```

### Camera not detected
- Check camera is connected
- Try different camera index (0, 1, 2)
- System will use test mode if no cameras found

### LED strip not working
- Verify GPIO pin connection
- Run with sudo on Raspberry Pi
- Check wiring: Data→GPIO18, VCC→5V, GND→GND

## 📚 Full Documentation

See **README.md** for complete documentation including:
- Detailed hardware setup
- Traffic logic explanation
- API endpoints
- Production deployment
- Security considerations

## 🎯 Next Steps

1. **Test locally** - Start the system and explore the dashboard
2. **Review code** - Check the implementation in `traffic_control/`
3. **Deploy to Pi** - Transfer to Raspberry Pi and connect hardware
4. **Customize** - Adjust settings and logic as needed

## 💡 Key Features

✅ Automatic vehicle detection with OpenCV  
✅ Smart traffic light control  
✅ Real-time web dashboard  
✅ Event logging and history  
✅ Dual-direction management  
✅ Safety-first (never both green)  
✅ Configurable timing  
✅ Simulation mode for testing

---

**System is ready to use! Start with `.\start.ps1` (Windows) or `./start.sh` (Raspberry Pi)**

For questions, check README.md or review the code comments.
