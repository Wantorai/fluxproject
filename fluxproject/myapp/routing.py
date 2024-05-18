from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/data/', consumers.DataConsumer.as_asgi()),
]

# uvicorn fluxproject.asgi:application --host 127.0.0.1 --port 8000
