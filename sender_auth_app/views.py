from sender_auth_app.models import Sender
from rest_framework.views import APIView
from sender_auth_app.serializers import SenderSerializer, SenderAuthSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
import logging
from rest_framework.parsers import FormParser, MultiPartParser
from django.http import Http404

logger = logging.getLogger(__name__)


# Create your views here.
class SenderCreationAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @permission_classes([IsAuthenticated])
    def get(self, request, format=None):
        senders = Sender.objects.all()
        serializer = SenderSerializer(senders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SenderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            sender = Sender.objects.get(
                username=serializer.validated_data.get("username")
            )
            sender.photo = request.data.get("file")
            sender.save()

            serializer.validated_data["photo_url"] = sender.photo.url
            serializer.save()
            refresh = RefreshToken.for_user(sender)
            return Response(
                {
                    "data": {
                        "data": serializer.data,
                        "access": str(refresh.access_token),
                    },
                    "status": True,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "data": serializer.errors,
                "status": False,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SenderDetailsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Sender.objects.get(pk=pk)
        except Sender.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        sender = self.get_object(pk=request.user.pk)
        serializer = SenderSerializer(sender)
        return Response(
            {
                "data": serializer.data,
                "status": True,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, format=None):
        sender = self.get_object(pk=request.user.pk)
        serializer = SenderSerializer(
            sender,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            if request.data.get("file") != None:
                sender.photo = request.data.get("file")
                sender.save()

                serializer.validated_data["photo_url"] = sender.photo.url
            serializer.save()
            return Response(
                {
                    "data": serializer.data,
                    "status": True,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "error": serializer.errors,
                    "status": False,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SenderAuthAPI(APIView):
    def post(self, request, format=None):
        serializer = SenderAuthSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            try:
                sender = Sender.objects.get(email=email, password=password)
            except Exception as e:
                return Response(
                    {
                        "message": "Sender doesn't exist",
                        "data": serializer.errors,
                        "status": False,
                    }
                )

            refresh = RefreshToken.for_user(sender)

            return Response(
                {
                    "data": {
                        "data": {
                            "id": sender.pk,
                            "first_name": sender.first_name,
                            "last_name": sender.last_name,
                            "email": sender.email,
                        },
                    },
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "status": True,
                }
            )

        return Response(
            {
                "message": "something went wrong",
                "data": serializer.errors,
                "status": False,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SenderLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"status": True}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"status": False}, status=status.HTTP_400_BAD_REQUEST)
