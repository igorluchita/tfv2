"""
Main Traffic Controller Module
Coordinates vehicle detection and traffic light control
"""
import threading
import time
import logging
from django.conf import settings
from .vehicle_detector import VehicleDetector
from .led_controller import LEDController
from .models import TrafficEvent, SystemStatus

logger = logging.getLogger('traffic_control')


class TrafficController:
    """Main controller for the smart traffic light system."""
    
    def __init__(self):
        """Initialize the traffic controller."""
        self.config = settings.TRAFFIC_CONFIG
        self.is_running = False
        self.control_thread = None
        
        # Initialize components
        self.detector_1 = VehicleDetector(
            camera_index=self.config['CAMERA_DIRECTION_1'],
            detection_threshold=self.config['DETECTION_THRESHOLD']
        )
        self.detector_2 = VehicleDetector(
            camera_index=self.config['CAMERA_DIRECTION_2'],
            detection_threshold=self.config['DETECTION_THRESHOLD']
        )
        self.led_controller = LEDController(
            led_pin=self.config['LED_PIN'],
            led_count=self.config['LED_COUNT'],
            brightness=self.config['LED_BRIGHTNESS']
        )
        
        # Traffic state
        self.current_green_direction = None
        self.green_start_time = None
        
        logger.info("Traffic controller initialized")
    
    def start(self):
        """Start the traffic control system."""
        if self.is_running:
            logger.warning("Traffic controller already running")
            return
        
        try:
            # Start cameras
            logger.info("Initializing vehicle detection...")
            cam1_ok = self.detector_1.start()
            cam2_ok = self.detector_2.start()
            
            if not cam1_ok and not cam2_ok:
                logger.info("No cameras detected. Running in SIMULATION mode with test data.")
            
            # Start LED controller
            logger.info("Starting LED controller...")
            self.led_controller.start()
            
            # Start control loop in separate thread
            self.is_running = True
            self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
            self.control_thread.start()
            
            logger.info("Traffic control system started successfully")
            
        except Exception as e:
            logger.error(f"Error starting traffic control system: {e}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the traffic control system."""
        logger.info("Stopping traffic control system...")
        self.is_running = False
        
        # Wait for control thread to finish
        if self.control_thread and self.control_thread.is_alive():
            self.control_thread.join(timeout=5)
        
        # Stop components
        self.detector_1.stop()
        self.detector_2.stop()
        self.led_controller.stop()
        
        logger.info("Traffic control system stopped")
    
    def _control_loop(self):
        """Main control loop that runs in a separate thread."""
        logger.info("Control loop started")
        
        # Initial state: both lights RED
        self.led_controller.set_red('direction_1')
        self.led_controller.set_red('direction_2')
        
        while self.is_running:
            try:
                # Check for vehicles in both directions
                if self.detector_1.is_active or self.detector_2.is_active:
                    # At least one camera is working
                    vehicles_1, _ = self.detector_1.detect_vehicles()
                    vehicles_2, _ = self.detector_2.detect_vehicles()
                else:
                    # No cameras - use simulation mode
                    vehicles_1 = self.detector_1.get_test_detection()
                    vehicles_2 = self.detector_2.get_test_detection()
                
                # Update system status
                self._update_status(vehicles_1, vehicles_2)
                
                # Traffic logic
                if self.current_green_direction is None:
                    # No green light active, check for vehicles
                    if vehicles_1 > 0:
                        self._switch_to_green('direction_1', vehicles_1)
                    elif vehicles_2 > 0:
                        self._switch_to_green('direction_2', vehicles_2)
                
                else:
                    # Green light is active
                    current_time = time.time()
                    green_duration = current_time - self.green_start_time
                    
                    # Check if minimum green time has passed
                    if green_duration >= self.config['MIN_GREEN_TIME']:
                        # Check if we should switch
                        if self.current_green_direction == 'direction_1':
                            if vehicles_1 == 0:
                                # No more vehicles in direction 1
                                self._switch_to_red('direction_1')
                                if vehicles_2 > 0:
                                    self._switch_to_green('direction_2', vehicles_2)
                            elif green_duration >= self.config['MAX_GREEN_TIME']:
                                # Max time reached, switch anyway
                                self._switch_to_red('direction_1')
                                if vehicles_2 > 0:
                                    self._switch_to_green('direction_2', vehicles_2)
                        
                        elif self.current_green_direction == 'direction_2':
                            if vehicles_2 == 0:
                                # No more vehicles in direction 2
                                self._switch_to_red('direction_2')
                                if vehicles_1 > 0:
                                    self._switch_to_green('direction_1', vehicles_1)
                            elif green_duration >= self.config['MAX_GREEN_TIME']:
                                # Max time reached, switch anyway
                                self._switch_to_red('direction_2')
                                if vehicles_1 > 0:
                                    self._switch_to_green('direction_1', vehicles_1)
                
                # Sleep before next check
                time.sleep(self.config['CHECK_INTERVAL'])
                
            except Exception as e:
                logger.error(f"Error in control loop: {e}")
                time.sleep(1)
        
        # Ensure all lights are red when stopping
        self.led_controller.set_red('direction_1')
        self.led_controller.set_red('direction_2')
        logger.info("Control loop ended")
    
    def _switch_to_green(self, direction, vehicle_count):
        """
        Switch specified direction to GREEN.
        
        Args:
            direction: 'direction_1' or 'direction_2'
            vehicle_count: Number of vehicles detected
        """
        self.current_green_direction = direction
        self.green_start_time = time.time()
        self.led_controller.set_green(direction)
        
        # Log event
        direction_name = 'DIRECTION_1' if direction == 'direction_1' else 'DIRECTION_2'
        TrafficEvent.objects.create(
            direction=direction_name,
            event_type='LIGHT_CHANGE',
            description=f'Light changed to GREEN for {direction_name}',
            vehicles_detected=vehicle_count,
            light_state='GREEN'
        )
        
        logger.info(f"{direction} switched to GREEN ({vehicle_count} vehicles detected)")
    
    def _switch_to_red(self, direction):
        """
        Switch specified direction to RED.
        
        Args:
            direction: 'direction_1' or 'direction_2'
        """
        self.led_controller.set_red(direction)
        self.current_green_direction = None
        self.green_start_time = None
        
        # Log event
        direction_name = 'DIRECTION_1' if direction == 'direction_1' else 'DIRECTION_2'
        TrafficEvent.objects.create(
            direction=direction_name,
            event_type='LIGHT_CHANGE',
            description=f'Light changed to RED for {direction_name}',
            light_state='RED'
        )
        
        logger.info(f"{direction} switched to RED")
    
    def _update_status(self, vehicles_1, vehicles_2):
        """
        Update system status in database.
        
        Args:
            vehicles_1: Number of vehicles in direction 1
            vehicles_2: Number of vehicles in direction 2
        """
        try:
            status, created = SystemStatus.objects.get_or_create(pk=1)
            status.is_running = self.is_running
            status.direction_1_light = self.led_controller.get_state('direction_1')
            status.direction_2_light = self.led_controller.get_state('direction_2')
            status.direction_1_vehicles = vehicles_1
            status.direction_2_vehicles = vehicles_2
            status.save()
        except Exception as e:
            logger.error(f"Error updating status: {e}")
