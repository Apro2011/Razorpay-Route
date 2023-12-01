from route.models import Reciever
from rest_framework import serializers


class RecieverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        fields = "__all__"
