from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/status/', views.get_status, name='get_status'),
    path('api/events/', views.get_events, name='get_events'),
    path('api/start/', views.start_system, name='start_system'),
    path('api/stop/', views.stop_system, name='stop_system'),
]
