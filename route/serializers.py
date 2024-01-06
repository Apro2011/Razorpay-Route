from route.models import Reciever, RecieversGroup, Payment, TransactionHistory
from rest_framework import serializers


class RecieversGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecieversGroup
        exclude = ["photo"]


class RecieverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        exclude = ["photo"]


class RecieverDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        exclude = ["photo"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"
