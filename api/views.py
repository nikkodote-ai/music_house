from django.shortcuts import render
from rest_framework import generics, status

from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room
from rest_framework.views import APIView 
from rest_framework.response import Response
from django.http import JsonResponse

# Create your views here.
# a view setup to return all of the different rooms
class RoomView(generics.ListAPIView):
    # what we want to return
    queryset = Room.objects.all()
    # the RoomSerializer that knows how to handle the python model to json, then change urls.py
    serializer_class = RoomSerializer


class JoinRoom(APIView):
    lookup_url_kwarg = 'code'

    def post(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                #make a note in backend to say this user is in this room
                self.request.session['room_code'] = code
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)

            return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Bad Request': 'Invalid post data, did not find a code key'}, status=status.HTTP_400_BAD_REQUEST)

class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'

    def get(self, request, format = None):
        code= request.GET.get(self.lookup_url_kwarg)
        if code != None:
            #code is unique and room is expected to be 1
            room = Room.objects.filter(code = code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status = status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code'}, status = status.HTTP_200_OK)
        
        return Response({'Bad Request': 'Code parameter not found in request'}, status  =status.HTTP_200_OK)

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
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                # fields we want to force udate
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            
            #ELSE, MAKING A NEW ROOM
            else:
                room = Room(host = host, guest_can_pause = guest_can_pause, votes_to_skip = votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code
            #returna  json formatted data
            return Response(RoomSerializer(room).data, status = status.HTTP_200_OK)
        
        
class UserInRoom(APIView):
    # get request to this endpoint ad check if user is in room and return the room code
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        data = {
            'code': self.request.session.get('room_code')
        }
        return JsonResponse(data, status=status.HTTP_200_OK)
    
class LeaveRoom(APIView):
    #update/changing data in the server: removing user in the room therefore POST
    def post(self, request, format=None):
        if 'room_code' in self.request.session:
            #remove room_code in the session
            self.request.session.pop('room_code')
            #get host id
            host_id = self.request.session.session_key
            #if host is hosting, then delete room
            room_results = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()

        return Response({'Message': 'Success'}, status=status.HTTP_200_OK)