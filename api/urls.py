from .views import *
from django.urls import path

urlpatterns = [
    path('room', RoomView.as_view())
]
