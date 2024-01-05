from route.models import Reciever, RecieversGroup, Payment
from rest_framework import serializers


class RecieversGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecieversGroup
        exclude = ["photo", "photo_url"]


class RecieverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        exclude = ["photo", "photo_url"]


class RecieverDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        exclude = ["photo", "photo_url"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
