from sender_auth_app.models import Sender
from rest_framework import serializers


class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sender
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "username",
            "photo_url",
        ]


class SenderAuthSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()
