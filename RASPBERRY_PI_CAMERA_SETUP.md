# Raspberry Pi Camera Module Setup Guide

## 📷 Using Raspberry Pi Camera Module 3

This system is optimized for **Raspberry Pi Camera Module 3** (12MP autofocus) on Raspberry Pi 5 with dual camera support.

### **Camera Module 3 Features:**
- 12MP Sony IMX708 sensor
- Autofocus
- HDR support
- Better low-light performance
- Phase detection autofocus (PDAF)

---

## 🔌 Hardware Setup

### **Connecting Camera Modules:**

**For Raspberry Pi 5 (2 CSI ports) - RECOMMENDED:**
- Camera Module 3 #1 → CSI Port 0 (labeled CAM0 or CAMERA)
- Camera Module 3 #2 → CSI Port 1 (labeled CAM1 or DISPLAY)

**Important:** Make sure the ribbon cable is:
- Inserted fully into both connectors
- Blue side facing away from the board
- Connector locks are closed properly

**For Raspberry Pi 4 (1 CSI port):**
- Camera Module 1 → CSI Port
- Camera Module 2 → Requires USB adapter or second Pi

### **LED Strip Connection:**
- Data Pin → GPIO 18 (Physical Pin 12)
- VCC → 5V (Physical Pin 2 or 4)
- GND → Ground (Physical Pin 6)

---

## ⚙️ Software Configuration

### **1. Enable Camera Interface:**

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options** → **Camera** → **Enable**
- Reboot after enabling: `sudo reboot`

### **2. Verify Camera Module 3 Detection:**

```bash
# Using libcamera (BEST for Camera Module 3)
libcamera-hello --list-cameras

# Should show both cameras:
# Available cameras
# 0 : imx708 [4608x2592] (/base/axi/pcie@120000/rp1/i2c@80000/imx708@1a)
# 1 : imx708 [4608x2592] (/base/axi/pcie@120000/rp1/i2c@88000/imx708@1a)

# List video devices
ls -l /dev/video*

# Using v4l-utils
v4l2-ctl --list-devices
```

### **3. Test Camera Module 3:**

```bash
# Quick test with libcamera
libcamera-hello --camera 0 -t 5000  # 5 second preview on Camera 0
libcamera-hello --camera 1 -t 5000  # 5 second preview on Camera 1

# Capture test images
libcamera-still -o test_cam0.jpg --camera 0
libcamera-still -o test_cam1.jpg --camera 1

# Test with Python/OpenCV
python3 << 'EOF'
import cv2
print("Testing Camera Module 3...")
cap = cv2.VideoCapture(0, cv2.CAP_ANY)
if cap.isOpened():
    print("✓ Camera 0: OK")
    ret, frame = cap.read()
    if ret:
        print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        cv2.imwrite("test_cam0_opencv.jpg", frame)
    cap.release()
else:
    print("✗ Camera 0: FAILED")

cap = cv2.VideoCapture(1, cv2.CAP_ANY)
if cap.isOpened():
    print("✓ Camera 1: OK")
    ret, frame = cap.read()
    if ret:
        print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
        cv2.imwrite("test_cam1_opencv.jpg", frame)
    cap.release()
else:
    print("✗ Camera 1: FAILED")
EOF
```

---

## 🚀 Running the System

### **Installation:**

```bash
cd ~/lab\ refacut

# Run setup script
bash setup-raspberry-pi.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-rpi.txt
python manage.py migrate
```

### **Start the System:**

```bash
# Must use sudo for GPIO access
sudo venv/bin/python manage.py runserver 0.0.0.0:8000
```

### **Access Dashboard:**

```
http://<raspberry-pi-ip>:8000
http://10.193.210.240:8000
```

---

## 🔧 Configuration

### **Camera Settings in `settings.py`:**

```python
TRAFFIC_CONFIG = {
    'CAMERA_DIRECTION_1': 0,    # First camera module (/dev/video0)
    'CAMERA_DIRECTION_2': 1,    # Second camera module (/dev/video1)
    # ... other settings
}
```

### **Camera Module 3 Configuration:**

The Camera Module 3 typically appears as:
- `/dev/video0` → Camera on CAM0 port
- `/dev/video1` → Camera on CAM1 port

If your cameras are numbered differently:
```bash
# Find camera indices
libcamera-hello --list-cameras
v4l2-ctl --list-devices
```

Then edit `traffic_system/settings.py`:
```python
TRAFFIC_CONFIG = {
    'CAMERA_DIRECTION_1': 0,  # Adjust if needed
    'CAMERA_DIRECTION_2': 1,  # Adjust if needed
    # ...
}
```

---

## 🐛 Troubleshooting

### **Camera Not Detected:**

```bash
# Check if camera interface is enabled
vcgencmd get_camera

# Should show: supported=1 detected=1

# Check kernel modules
lsmod | grep bcm2835_v4l2

# Load module manually if needed
sudo modprobe bcm2835_v4l2
```

### **Permission Errors:**

```bash
# Add user to video group
sudo usermod -a -G video $USER

# Add user to gpio group
sudo usermod -a -G gpio $USER

# Logout and login again
```

### **Camera Module 3 Not Working:**

1. **Check physical connection**
   - Ribbon cable fully inserted on both ends
   - Blue side facing AWAY from the board
   - Connector locks closed properly
   - Try reseating the cable

2. **Check camera detection**
   ```bash
   # Should show both imx708 cameras
   libcamera-hello --list-cameras
   
   # Check system logs
   dmesg | grep imx708
   ```

3. **Update Raspberry Pi OS and firmware** (IMPORTANT for Camera Module 3)
   ```bash
   sudo apt update
   sudo apt full-upgrade -y
   sudo rpi-update  # Update firmware
   sudo reboot
   ```

4. **Check config.txt settings**
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
   
   Ensure you have:
   ```ini
   # Enable cameras (should be automatic on Pi 5)
   camera_auto_detect=1
   
   # Do NOT use legacy camera for Camera Module 3
   # start_x=0  (make sure this is commented out or 0)
   ```

5. **Verify libcamera installation**
   ```bash
   libcamera-hello --version
   # Should show version 0.0.5 or higher
   
   # Reinstall if needed
   sudo apt install --reinstall libcamera-apps
   ```

### **Using libcamera Instead of V4L2:**

If you're on Raspberry Pi OS Bullseye or newer and cameras aren't working with V4L2:

Edit `vehicle_detector.py` to use libcamera-vid:
```python
# Use this for newer Raspberry Pi OS
from picamera2 import Picamera2

# Then replace VideoCapture with Picamera2
```

Or install compatibility layer:
```bash
sudo apt install libcamera-apps
sudo apt install python3-picamera2
```

---

## 📊 Camera Module Specifications

**Recommended Settings:**
- Resolution: 640x480 (for fast processing)
- FPS: 30
- Format: BGR/RGB

**Supported Modules:**
- Camera Module v1 (5MP)
- Camera Module v2 (8MP)
- Camera Module v3 (12MP)
- HQ Camera Module (12.3MP)

---

## 🎯 Testing Without Physical Cameras

The system will automatically fall back to simulation mode if cameras aren't detected. You can still test the dashboard and logic without hardware.

---

## 📝 Quick Reference

```bash
# Enable camera interface
sudo raspi-config

# Check cameras
ls -l /dev/video*
v4l2-ctl --list-devices
libcamera-hello --list-cameras

# Test camera capture
libcamera-still -o test.jpg --camera 0

# Install dependencies
bash setup-raspberry-pi.sh

# Start system
sudo venv/bin/python manage.py runserver 0.0.0.0:8000

# View logs
tail -f traffic_system.log
```

---

## 🔗 Useful Links

- [Raspberry Pi Camera Setup](https://www.raspberrypi.com/documentation/computers/camera_software.html)
- [libcamera Documentation](https://libcamera.org/)
- [Picamera2 Library](https://github.com/raspberrypi/picamera2)

---

**Your system is now configured for Raspberry Pi Camera Modules!** 📷🚦
