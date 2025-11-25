"""
Vehicle Detection Module using OpenCV
Detects vehicles in video stream from cameras
"""
import cv2
import numpy as np
import logging
from datetime import datetime

logger = logging.getLogger('traffic_control')


class VehicleDetector:
    """Detects vehicles using OpenCV's pre-trained models."""
    
    def __init__(self, camera_index=0, detection_threshold=0.3):
        """
        Initialize vehicle detector.
        
        Args:
            camera_index: Camera device index
            detection_threshold: Confidence threshold for detection (0-1)
        """
        self.camera_index = camera_index
        self.detection_threshold = detection_threshold
        self.cap = None
        self.is_active = False
        
        # Load YOLO or use Haar Cascades (simplified for this example)
        # In production, use YOLOv5/v8 or MobileNet SSD for better accuracy
        # Note: haarcascade_car.xml is not included in OpenCV by default
        self.car_cascade = None  # Disabled - use motion detection instead
        
        # Background subtractor for motion detection as fallback
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=16,
            detectShadows=True
        )
    
    def start(self):
        """Start the camera capture."""
        try:
            # Suppress OpenCV warnings during camera initialization
            import os
            os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
            
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.info(f"Camera {self.camera_index} not available (simulation mode)")
                return False
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_active = True
            logger.info(f"Camera {self.camera_index} started successfully")
            return True
        except Exception as e:
            logger.info(f"Camera {self.camera_index} not available: {e}")
            return False
    
    def stop(self):
        """Stop the camera capture and release resources."""
        self.is_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info(f"Camera {self.camera_index} stopped")
    
    def detect_vehicles(self):
        """
        Detect vehicles in the current frame.
        
        Returns:
            tuple: (vehicle_count, frame) - Number of vehicles detected and the frame
        """
        if not self.is_active or not self.cap:
            return 0, None
        
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                # Camera not working - return 0 silently
                return 0, None
            
            # Use motion-based detection
            # For production on Raspberry Pi, replace with YOLO or MobileNet SSD
            vehicle_count = self._detect_by_motion(frame)
            
            return vehicle_count, frame
            
        except Exception as e:
            logger.error(f"Error detecting vehicles: {e}")
            return 0, None
    
    def _detect_by_motion(self, frame):
        """
        Detect vehicles based on motion.
        
        Args:
            frame: Current video frame
            
        Returns:
            int: Estimated number of vehicles (0 or 1 for simplified detection)
        """
        try:
            # Apply background subtraction
            fg_mask = self.bg_subtractor.apply(frame)
            
            # Remove shadows and noise
            _, fg_mask = cv2.threshold(fg_mask, 244, 255, cv2.THRESH_BINARY)
            
            # Morphological operations to remove noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(
                fg_mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Count significant contours (potential vehicles)
            min_area = 1000  # Minimum area for a vehicle
            vehicle_count = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    vehicle_count += 1
                    # Draw bounding box
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            return vehicle_count
            
        except Exception as e:
            logger.error(f"Error in motion detection: {e}")
            return 0
    
    def get_test_detection(self):
        """
        Simulate vehicle detection for testing without cameras.
        
        Returns:
            int: Random vehicle count (0 or 1)
        """
        import random
        return random.choice([0, 0, 0, 1])  # 25% chance of detecting a vehicle
