from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import TrafficEvent, SystemStatus
from .traffic_controller import TrafficController
from .vehicle_detector import VehicleDetector
import json
import cv2
import time

# Global traffic controller instance
traffic_controller = None

# Global camera instances for video streaming
stream_camera_1 = None
stream_camera_2 = None


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
    global traffic_controller, stream_camera_1, stream_camera_2
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        if traffic_controller:
            traffic_controller.stop()
            traffic_controller = None
        
        # Stop streaming cameras
        if stream_camera_1:
            stream_camera_1.stop()
            stream_camera_1 = None
        if stream_camera_2:
            stream_camera_2.stop()
            stream_camera_2 = None
        
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


def generate_frames(camera_index):
    """Generate frames for video streaming."""
    global stream_camera_1, stream_camera_2
    
    # Get or create camera instance
    if camera_index == 0:
        if stream_camera_1 is None:
            from django.conf import settings
            stream_camera_1 = VehicleDetector(
                camera_index=settings.TRAFFIC_CONFIG['CAMERA_DIRECTION_1']
            )
            stream_camera_1.start()
        camera = stream_camera_1
    else:
        if stream_camera_2 is None:
            from django.conf import settings
            stream_camera_2 = VehicleDetector(
                camera_index=settings.TRAFFIC_CONFIG['CAMERA_DIRECTION_2']
            )
            stream_camera_2.start()
        camera = stream_camera_2
    
    while True:
        try:
            if camera and camera.is_active:
                vehicle_count, frame = camera.detect_vehicles()
                
                if frame is not None:
                    # Add vehicle count overlay
                    cv2.putText(frame, f'Vehicles: {vehicle_count}', 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                               1, (0, 255, 0), 2)
                    
                    # Add camera label
                    label = f'Camera {camera_index + 1}'
                    cv2.putText(frame, label, 
                               (10, frame.shape[0] - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, (255, 255, 255), 2)
                    
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, 
                                              [cv2.IMWRITE_JPEG_QUALITY, 85])
                    
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    # No frame available - send placeholder
                    time.sleep(0.1)
            else:
                # Camera not active - send placeholder or break
                time.sleep(0.1)
        except Exception as e:
            print(f"Error generating frame: {e}")
            time.sleep(0.1)


def video_feed_1(request):
    """Video streaming endpoint for camera 1."""
    return StreamingHttpResponse(
        generate_frames(0),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


def video_feed_2(request):
    """Video streaming endpoint for camera 2."""
    return StreamingHttpResponse(
        generate_frames(1),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )
