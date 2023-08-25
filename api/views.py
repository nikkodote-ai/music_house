from django.shortcuts import render
from rest_framework import generics

from .serializers import RoomSerializer
from .models import Room


# Create your views here.
# a view setup to return all of the different rooms
class RoomView(generics.CreateAPIView):
    # what we want to return
    queryset = Room.objects.all()
    # the RoomSerializer that knows how to handle the python model to json, then change urls.py
    serializer_class = RoomSerializer