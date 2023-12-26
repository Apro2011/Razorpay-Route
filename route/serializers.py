from route.models import Reciever, RecieversGroup, Payment
from rest_framework import serializers


class RecieversGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecieversGroup
        fields = "__all__"


class RecieverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        fields = "__all__"


class RecieverDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        fields = ["percentage"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
