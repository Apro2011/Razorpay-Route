from sender_auth_app.models import Sender
from rest_framework import serializers


class SenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sender
        fields = ["username", "email"]
