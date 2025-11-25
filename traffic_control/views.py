from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import TrafficEvent, SystemStatus
from .traffic_controller import TrafficController
import json

# Global traffic controller instance
traffic_controller = None


def dashboard(request):
    """Main dashboard view."""
    try:
        status = SystemStatus.objects.first()
        if not status:
            status = SystemStatus.objects.create()
    except Exception:
        status = None
    
    recent_events = TrafficEvent.objects.all()[:20]
    
    context = {
        'status': status,
        'recent_events': recent_events,
    }
    return render(request, 'dashboard.html', context)


def get_status(request):
    """API endpoint to get current system status."""
    try:
        status = SystemStatus.objects.first()
        if not status:
            status = SystemStatus.objects.create()
        
        data = {
            'is_running': status.is_running,
            'direction_1_light': status.direction_1_light,
            'direction_2_light': status.direction_2_light,
            'direction_1_vehicles': status.direction_1_vehicles,
            'direction_2_vehicles': status.direction_2_vehicles,
            'last_update': status.last_update.isoformat(),
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_events(request):
    """API endpoint to get recent traffic events."""
    try:
        limit = int(request.GET.get('limit', 50))
        hours = int(request.GET.get('hours', 24))
        
        since = timezone.now() - timedelta(hours=hours)
        events = TrafficEvent.objects.filter(timestamp__gte=since)[:limit]
        
        data = {
            'events': [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'direction': event.direction,
                    'event_type': event.event_type,
                    'description': event.description,
                    'vehicles_detected': event.vehicles_detected,
                    'light_state': event.light_state,
                }
                for event in events
            ]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def start_system(request):
    """API endpoint to start the traffic control system."""
    global traffic_controller
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        if traffic_controller and traffic_controller.is_running:
            return JsonResponse({'message': 'System already running'})
        
        traffic_controller = TrafficController()
        traffic_controller.start()
        
        # Update system status
        status = SystemStatus.objects.first()
        if not status:
            status = SystemStatus.objects.create()
        status.is_running = True
        status.save()
        
        # Log event
        TrafficEvent.objects.create(
            direction='BOTH',
            event_type='SYSTEM_START',
            description='Traffic control system started'
        )
        
        return JsonResponse({'message': 'System started successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def stop_system(request):
    """API endpoint to stop the traffic control system."""
    global traffic_controller
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        if traffic_controller:
            traffic_controller.stop()
            traffic_controller = None
        
        # Update system status
        status = SystemStatus.objects.first()
        if status:
            status.is_running = False
            status.direction_1_light = 'RED'
            status.direction_2_light = 'RED'
            status.save()
        
        # Log event
        TrafficEvent.objects.create(
            direction='BOTH',
            event_type='SYSTEM_STOP',
            description='Traffic control system stopped'
        )
        
        return JsonResponse({'message': 'System stopped successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
