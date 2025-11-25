from django.contrib import admin
from .models import TrafficEvent, SystemStatus


@admin.register(TrafficEvent)
class TrafficEventAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'direction', 'event_type', 'vehicles_detected']
    list_filter = ['direction', 'event_type', 'timestamp']
    search_fields = ['description']
    ordering = ['-timestamp']


@admin.register(SystemStatus)
class SystemStatusAdmin(admin.ModelAdmin):
    list_display = ['is_running', 'direction_1_light', 'direction_2_light', 'last_update']
    list_filter = ['is_running']
    ordering = ['-last_update']
