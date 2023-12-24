from sender_auth_app.models import Sender
from rest_framework.views import APIView
from sender_auth_app.serializers import SenderSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class SenderCreationAPI(APIView):
    def post(self, request, format=None):
        serializer = SenderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SenderAuthAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        senders = Sender.objects.all()
        serializer = SenderSerializer(senders, many=True)
        return Response(serializer.data)
