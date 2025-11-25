from django.db import models
from django.utils import timezone


class TrafficEvent(models.Model):
    """Model to log traffic events and light changes."""
    
    EVENT_TYPES = [
        ('LIGHT_CHANGE', 'Light Change'),
        ('VEHICLE_DETECTED', 'Vehicle Detected'),
        ('NO_VEHICLE', 'No Vehicle'),
        ('SYSTEM_START', 'System Start'),
        ('SYSTEM_STOP', 'System Stop'),
        ('ERROR', 'Error'),
    ]
    
    DIRECTIONS = [
        ('DIRECTION_1', 'Direction 1'),
        ('DIRECTION_2', 'Direction 2'),
        ('BOTH', 'Both Directions'),
    ]
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    direction = models.CharField(max_length=20, choices=DIRECTIONS)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    vehicles_detected = models.IntegerField(default=0)
    light_state = models.CharField(max_length=10, blank=True)  # RED, GREEN
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['direction', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.direction} - {self.event_type}"


class SystemStatus(models.Model):
    """Model to store current system status."""
    
    is_running = models.BooleanField(default=False)
    direction_1_light = models.CharField(max_length=10, default='RED')
    direction_2_light = models.CharField(max_length=10, default='RED')
    direction_1_vehicles = models.IntegerField(default=0)
    direction_2_vehicles = models.IntegerField(default=0)
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "System Status"
    
    def __str__(self):
        return f"System Status - Running: {self.is_running}"
