from route.models import Reciever
from django.contrib.auth.models import Group
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class RecieverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        exclude = ["password"]
