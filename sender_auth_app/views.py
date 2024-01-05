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

logger = logging.getLogger(__name__)


# Create your views here.
class SenderCreationAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @permission_classes([IsAuthenticated])
    def put(self, request, format=None):
        try:
            senders = Sender.objects.all()
            serializer = SenderSerializer(senders, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response(
                {"error": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, format=None):
        serializer = SenderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            sender = Sender.objects.get(
                username=serializer.validated_data.get("username")
            )
            sender.photo = request.data.get("file")
            sender.save()
            sender.photo_url = request.build_absolute_uri(sender.photo.url)
            sender.save()
            refresh = RefreshToken.for_user(sender)
            return Response(
                {
                    "data": {
                        "data": serializer.data,
                        "image_url": sender.photo_url,
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


class SenderAuthAPI(APIView):
    def post(self, request, format=None):
        serializer = SenderAuthSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            try:
                sender = Sender.objects.get(email=email, password=password)
                print(sender.photo_url)
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
                        "image_url": sender.photo_url,
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
