from route.models import Reciever, Stakeholder, ProductConfigDetails
from route.serializers import (
    RecieverSerializer,
    GroupSerializer,
    StakeholderSerializer,
    ProductConfigDetailsSerializer,
    UpdateProductConfigDetailsSerializer,
)
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
import json
import requests
from core import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


# Create your views here.
class CreatingGroup(APIView):
    def get(self, request, format=None):
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            reciever_content_type = ContentType.objects.get_for_model(Reciever)
            add_permission = Permission.objects.get(
                codename="add_reciever", content_type=reciever_content_type
            )
            change_permission = Permission.objects.get(
                codename="change_reciever", content_type=reciever_content_type
            )
            delete_permission = Permission.objects.get(
                codename="delete_reciever", content_type=reciever_content_type
            )
            Group.objects.get(
                name=serializer.validated_data.get("name")
            ).permissions.add(add_permission, change_permission, delete_permission)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecieverList(APIView):
    def get(self, request, format=None):
        recievers = Reciever.objects.all()
        serializer = RecieverSerializer(recievers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RecieverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            group = Group.objects.get(name=serializer.validated_data.get("group_name"))
            reciever = Reciever.objects.get(
                username=serializer.validated_data.get("username")
            )
            reciever.groups.add(group)
            serializer.save()

            # Create Linked Accounts
            accounts_url = "https://api.razorpay.com/v2/accounts"
            account_data = {
                "email": serializer.validated_data.get("email"),
                "phone": serializer.validated_data.get("phone"),
                "type": serializer.validated_data.get("type"),
                "reference_id": serializer.validated_data.get("reference_id"),
                "legal_business_name": serializer.validated_data.get(
                    "legal_business_name"
                ),
                "business_type": serializer.validated_data.get("business_type"),
                "contact_name": serializer.validated_data.get("contact_name"),
                "profile": {
                    "category": serializer.validated_data.get("category"),
                    "subcategory": serializer.validated_data.get("subcategory"),
                    "addresses": {
                        "registered": {
                            "street1": serializer.validated_data.get("street1"),
                            "street2": serializer.validated_data.get("street2"),
                            "city": serializer.validated_data.get("city"),
                            "state": serializer.validated_data.get("state"),
                            "postal_code": serializer.validated_data.get("postal_code"),
                            "country": serializer.validated_data.get("country"),
                        }
                    },
                },
                "legal_info": {
                    "pan": serializer.validated_data.get("pan"),
                    "gst": serializer.validated_data.get("gst"),
                },
            }

            account_response = requests.post(
                accounts_url,
                auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
                headers={"Content-Type": "application/json"},
                json=account_data,
            )

            razor_id = json.loads(account_response.content.decode("utf-8"))["id"]
            serializer.validated_data["razor_id"] = razor_id
            serializer.save()

            return Response(account_response.json(), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateStakeholder(APIView):
    def get(self, request, format=None):
        stakeholders = Stakeholder.objects.all()
        serializer = StakeholderSerializer(stakeholders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = StakeholderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            reciever_instance = serializer.validated_data.get("linked_account")
            razor_id = reciever_instance.razor_id
            stakeholder_url = (
                "https://api.razorpay.com/v2/accounts/" + razor_id + "/stakeholders"
            )

            # Create Stakeholder account
            stakeholder_data = {
                "name": serializer.validated_data["name"],
                "email": serializer.validated_data["email"],
                "addresses": {
                    "residential": {
                        "street": serializer.validated_data["street"],
                        "city": serializer.validated_data["city"],
                        "state": serializer.validated_data["state"],
                        "postal_code": serializer.validated_data["postal_code"],
                        "country": serializer.validated_data["country"],
                    }
                },
                "kyc": {"pan": serializer.validated_data["pan"]},
                "notes": {"random_key": "random_value"},
            }

            stakeholder_response = requests.post(
                stakeholder_url,
                auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
                headers={"Content-Type": "application/json"},
                json=stakeholder_data,
            )

            return Response(stakeholder_response.json(), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductConfiguration(APIView):
    def get(self, request, format=None):
        products = ProductConfigDetails.objects.all()
        serializer = ProductConfigDetailsSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductConfigDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            reciever_instance = serializer.validated_data.get("linked_account")
            razor_id = reciever_instance.razor_id
            product_config_url = (
                "https://api.razorpay.com/v2/accounts/" + razor_id + "/products"
            )

            # Request Product Configuration
            product_config_data = {
                "product_name": serializer.validated_data.get("product_name"),
                "tnc_accepted": serializer.validated_data.get("tnc_accepted"),
            }

            product_config_response = requests.post(
                product_config_url,
                auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
                headers={"Content-Type": "application/json"},
                json=product_config_data,
            )

            product_id = json.loads(product_config_response.content.decode("utf-8"))[
                "id"
            ]
            serializer.validated_data["product_id"] = product_id
            serializer.save()

            return Response(
                product_config_response.json(), status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProductConfiguration(APIView):
    def get_object(self, pk):
        try:
            return ProductConfigDetails.objects.get(pk=pk)
        except ProductConfigDetails.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = UpdateProductConfigDetailsSerializer(product)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        serializer = UpdateProductConfigDetailsSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            reciever_instance = serializer.validated_data.get("linked_account")
            razor_id = reciever_instance.razor_id
            product_id = product.product_id
            update_product_config_url = (
                "https://api.razorpay.com/v2/accounts/"
                + razor_id
                + "/products/"
                + product_id
                + "/"
            )

            # Request Update Product Configuration
            update_product_config_data = {
                "settlements": {
                    "account_number": serializer.validated_data.get("account_number"),
                    "ifsc_code": serializer.validated_data.get("ifsc_code"),
                    "beneficiary_name": serializer.validated_data.get(
                        "beneficiary_name"
                    ),
                },
                "tnc_accepted": serializer.validated_data.get("tnc_accepted"),
            }

            update_product_config_response = requests.patch(
                update_product_config_url,
                auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
                headers={"Content-Type": "application/json"},
                json=update_product_config_data,
            )

            return Response(
                update_product_config_response.json(), status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SplitPayments(APIView):
    def post(self, request, format=None):
        initial_amount = int(request.data.get("initial_amount")) * 100
        recievers_ids_and_percentages = request.data.get(
            "recievers_ids_and_percentages", []
        )
        client = razorpay.Client(
            auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
        )

        percentage_sum = 0
        for p in recievers_ids_and_percentages:
            percentage_sum += p[1]

        if percentage_sum != 100:
            return Response(
                {"message": "Sum of percentages should be equal to 100"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        accounts = []

        for reciever in recievers_ids_and_percentages:
            reciever_amount = initial_amount * (reciever[1] / 100)
            account = Reciever.objects.get(bank_account=reciever[0])
            account.payment = reciever_amount
            account.percentage = reciever[1]
            account.save()
            accounts.append(account)

        transfer_list = []
        for a in accounts:
            transfer_list.append(
                {
                    "account": a.razor_id,
                    "amount": int(a.payment),
                    "currency": "INR",
                    "on_hold": 0,
                }
            )

        transfer = client.order.create(
            {
                "amount": int(initial_amount),
                "currency": "INR",
                "transfers": [_ for _ in transfer_list],
            }
        )

        return Response(transfer, status=status.HTTP_202_ACCEPTED)
