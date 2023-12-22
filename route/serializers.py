from route.models import Reciever, Stakeholder, ProductConfigDetails
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


class RecieverDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reciever
        fields = ["percentage"]


class StakeholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholder
        fields = "__all__"


class ProductConfigDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfigDetails
        fields = "__all__"


class UpdateProductConfigDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConfigDetails
        fields = [
            "main_id",
            "linked_account",
            "account_number",
            "ifsc_code",
            "beneficiary_name",
            "tnc_accepted",
        ]
