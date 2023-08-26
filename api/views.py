from django.shortcuts import render
from rest_framework import generics, status

from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room
from rest_framework.views import APIView 
from rest_framework.response import Response


# Create your views here.
# a view setup to return all of the different rooms
class RoomView(generics.ListAPIView):
    # what we want to return
    queryset = Room.objects.all()
    # the RoomSerializer that knows how to handle the python model to json, then change urls.py
    serializer_class = RoomSerializer

class CreateRoomView(APIView):
    #serializer class is important to recognize the data. if the form is not rendered correctly, you might have missed this
    serializer_class = CreateRoomSerializer

    def post(self, request, format = None):
        # check if there is an exiting session, if there isn't, make one
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            #instead of making a new one right away, check if there is
            #an existing room with the current host

            #UPDATING existing room of host
            queryset = Room.objects.filter(host = host)
            if queryset.exist():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                # fields we want to force udate
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            
            #ELSE, MAKING A NEW ROOM
            else:
                room = Room(host = host, guest_can_pause = guest_can_pause, votes_to_skip = votes_to_skip)
                room.save()
            #returna  json formatted data
            return Response(RoomSerializer(room).data, status = status.HTTP_200)