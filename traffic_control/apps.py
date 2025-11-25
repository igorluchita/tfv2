from django.apps import AppConfig


class TrafficControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'traffic_control'

    def ready(self):
        """Initialize the traffic control system when the app is ready."""
        import traffic_control.signals
