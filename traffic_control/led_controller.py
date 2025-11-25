"""
LED Strip Controller Module
Controls addressable LED strip for traffic lights
"""
import logging
import platform

logger = logging.getLogger('traffic_control')

# Try to import LED library (only works on Raspberry Pi)
try:
    if platform.machine() in ['armv7l', 'aarch64', 'armv6l']:
        # Running on Raspberry Pi
        from rpi_ws281x import PixelStrip, Color
        REAL_LED = True
    else:
        REAL_LED = False
except ImportError:
    REAL_LED = False
    logger.warning("LED library not available. Running in simulation mode.")


class LEDController:
    """Controls the LED strip for traffic light display."""
    
    # LED strip configuration
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz
    LED_DMA = 10          # DMA channel to use for generating signal
    LED_INVERT = False    # True to invert the signal
    LED_CHANNEL = 0       # PWM channel
    
    # Colors (GRB format for WS2812B)
    COLOR_RED = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_YELLOW = (255, 255, 0)
    COLOR_OFF = (0, 0, 0)
    
    def __init__(self, led_pin=18, led_count=6, brightness=255):
        """
        Initialize LED controller.
        
        Args:
            led_pin: GPIO pin connected to the LED strip
            led_count: Total number of LEDs (3 per direction)
            brightness: LED brightness (0-255)
        """
        self.led_pin = led_pin
        self.led_count = led_count
        self.brightness = brightness
        self.strip = None
        self.is_active = False
        
        # LED assignments
        # Direction 1: LEDs 0-2 (Red=0, Yellow=1, Green=2)
        # Direction 2: LEDs 3-5 (Red=3, Yellow=4, Green=5)
        self.direction_1_leds = [0, 1, 2]  # Red, Yellow, Green
        self.direction_2_leds = [3, 4, 5]  # Red, Yellow, Green
        
        # Simulation mode state
        self.simulated_state = {
            'direction_1': 'RED',
            'direction_2': 'RED'
        }
    
    def start(self):
        """Initialize the LED strip."""
        try:
            if REAL_LED:
                self.strip = PixelStrip(
                    self.led_count,
                    self.led_pin,
                    self.LED_FREQ_HZ,
                    self.LED_DMA,
                    self.LED_INVERT,
                    self.brightness,
                    self.LED_CHANNEL
                )
                self.strip.begin()
                logger.info("LED strip initialized")
            else:
                logger.info("LED strip running in SIMULATION mode")
            
            self.is_active = True
            
            # Set initial state (all red)
            self.set_red('direction_1')
            self.set_red('direction_2')
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing LED strip: {e}")
            return False
    
    def stop(self):
        """Turn off all LEDs and cleanup."""
        try:
            if self.is_active:
                self.turn_off_all()
                self.is_active = False
                logger.info("LED strip stopped")
        except Exception as e:
            logger.error(f"Error stopping LED strip: {e}")
    
    def set_color(self, led_index, color):
        """
        Set a specific LED to a color.
        
        Args:
            led_index: Index of the LED
            color: Tuple (R, G, B)
        """
        if REAL_LED and self.strip:
            r, g, b = color
            self.strip.setPixelColor(led_index, Color(r, g, b))
            self.strip.show()
        else:
            # Simulation mode - just log
            pass
    
    def set_red(self, direction):
        """
        Set traffic light to RED for specified direction.
        
        Args:
            direction: 'direction_1' or 'direction_2'
        """
        try:
            if direction == 'direction_1':
                leds = self.direction_1_leds
            else:
                leds = self.direction_2_leds
            
            # Red LED on, others off
            self.set_color(leds[0], self.COLOR_RED)    # Red ON
            self.set_color(leds[1], self.COLOR_OFF)    # Yellow OFF
            self.set_color(leds[2], self.COLOR_OFF)    # Green OFF
            
            self.simulated_state[direction] = 'RED'
            logger.info(f"{direction}: Set to RED")
            
        except Exception as e:
            logger.error(f"Error setting RED light: {e}")
    
    def set_green(self, direction):
        """
        Set traffic light to GREEN for specified direction.
        
        Args:
            direction: 'direction_1' or 'direction_2'
        """
        try:
            if direction == 'direction_1':
                leds = self.direction_1_leds
            else:
                leds = self.direction_2_leds
            
            # Green LED on, others off
            self.set_color(leds[0], self.COLOR_OFF)    # Red OFF
            self.set_color(leds[1], self.COLOR_OFF)    # Yellow OFF
            self.set_color(leds[2], self.COLOR_GREEN)  # Green ON
            
            self.simulated_state[direction] = 'GREEN'
            logger.info(f"{direction}: Set to GREEN")
            
        except Exception as e:
            logger.error(f"Error setting GREEN light: {e}")
    
    def set_yellow(self, direction):
        """
        Set traffic light to YELLOW for specified direction.
        
        Args:
            direction: 'direction_1' or 'direction_2'
        """
        try:
            if direction == 'direction_1':
                leds = self.direction_1_leds
            else:
                leds = self.direction_2_leds
            
            # Yellow LED on, others off
            self.set_color(leds[0], self.COLOR_OFF)      # Red OFF
            self.set_color(leds[1], self.COLOR_YELLOW)   # Yellow ON
            self.set_color(leds[2], self.COLOR_OFF)      # Green OFF
            
            self.simulated_state[direction] = 'YELLOW'
            logger.info(f"{direction}: Set to YELLOW")
            
        except Exception as e:
            logger.error(f"Error setting YELLOW light: {e}")
    
    def turn_off_all(self):
        """Turn off all LEDs."""
        try:
            if REAL_LED and self.strip:
                for i in range(self.led_count):
                    self.strip.setPixelColor(i, Color(0, 0, 0))
                self.strip.show()
            
            self.simulated_state = {
                'direction_1': 'OFF',
                'direction_2': 'OFF'
            }
            logger.info("All LEDs turned off")
            
        except Exception as e:
            logger.error(f"Error turning off LEDs: {e}")
    
    def get_state(self, direction):
        """
        Get current light state for a direction.
        
        Args:
            direction: 'direction_1' or 'direction_2'
            
        Returns:
            str: Current state ('RED', 'GREEN', 'YELLOW', 'OFF')
        """
        return self.simulated_state.get(direction, 'RED')
