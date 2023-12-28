from sender_auth_app.models import Sender
from rest_framework.views import APIView
from sender_auth_app.serializers import SenderSerializer, SenderAuthSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class SenderCreationAPI(APIView):
    @permission_classes([IsAuthenticated])
    def get(self, request, format=None):
        senders = Sender.objects.all()
        serializer = SenderSerializer(senders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SenderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SenderAuthAPI(APIView):
    def post(self, request, format=None):
        serializer = SenderAuthSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            sender = Sender.objects.get(email=email, password=password)
            if sender is None:
                return Response(
                    {
                        "status": 400,
                        "message": "Sender doesn't exist",
                        "data": serializer.errors,
                    }
                )

            refresh = RefreshToken.for_user(sender)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )

        return Response(
            {
                "status": 400,
                "message": "something went wrong",
                "data": serializer.errors,
            }
        )


class SenderLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
