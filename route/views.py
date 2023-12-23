from route.models import Reciever
from route.serializers import (
    RecieverSerializer,
    RecieverDetailsSerializer,
    GroupSerializer,
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

            if account_response.status_code != 200:
                return Response(account_response.json(), status=status.HTTP_201_CREATED)
            else:
                razor_id = json.loads(account_response.content.decode("utf-8"))["id"]
                serializer.validated_data["razor_id"] = razor_id
                serializer.save()
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
                }

                stakeholder_response = requests.post(
                    stakeholder_url,
                    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
                    headers={"Content-Type": "application/json"},
                    json=stakeholder_data,
                )

                if stakeholder_response.status_code != 200:
                    return Response(
                        stakeholder_response.json(), status=status.HTTP_201_CREATED
                    )
                else:
                    product_config_url = (
                        "https://api.razorpay.com/v2/accounts/" + razor_id + "/products"
                    )

                    # Request Product Configuration
                    product_config_data = {
                        "product_name": serializer.validated_data.get("product_name"),
                        "tnc_accepted": serializer.validated_data.get("tnc_accepted"),
                        "tnc_accepted": serializer.validated_data.get("tnc_accepted"),
                    }

                    product_config_response = requests.post(
                        product_config_url,
                        auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
                        headers={"Content-Type": "application/json"},
                        json=product_config_data,
                    )

                    if product_config_response.status_code != 200:
                        return Response(
                            product_config_response.json(),
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        product_id = json.loads(
                            product_config_response.content.decode("utf-8")
                        )["id"]
                        serializer.validated_data["product_id"] = product_id
                        serializer.save()

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
                                "account_number": serializer.validated_data.get(
                                    "account_number"
                                ),
                                "ifsc_code": serializer.validated_data.get("ifsc_code"),
                                "beneficiary_name": serializer.validated_data.get(
                                    "beneficiary_name"
                                ),
                            },
                            "tnc_accepted": serializer.validated_data.get(
                                "tnc_accepted"
                            ),
                        }

                        update_product_config_response = requests.patch(
                            update_product_config_url,
                            auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
                            headers={"Content-Type": "application/json"},
                            json=update_product_config_data,
                        )

                        if update_product_config_response.status_code != 200:
                            return Response(
                                update_product_config_response.json(),
                                status=status.HTTP_201_CREATED,
                            )
                        else:
                            return Response(
                                [
                                    account_response.json(),
                                    stakeholder_response.json(),
                                    product_config_response.json(),
                                    update_product_config_response.json(),
                                ],
                                status=status.HTTP_201_CREATED,
                            )

        return Response(
            [serializer.errors, account_response.json()],
            status=status.HTTP_400_BAD_REQUEST,
        )


class RecieverDetails(APIView):
    def get_object(self, pk):
        try:
            return Reciever.objects.get(pk=pk)
        except Reciever.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        reciever = self.get_object(pk=pk)
        serializer = RecieverSerializer(reciever)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        reciever = self.get_object(pk=pk)
        serializer = RecieverDetailsSerializer(reciever, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SplitPayments(APIView):
    def post(self, request, format=None):
        initial_amount = int(request.data.get("initial_amount")) * 100
        group_name = request.data.get("group_name", [])

        reciever_list_in_group = Reciever.objects.filter(group_name=group_name)

        client = razorpay.Client(
            auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
        )

        percentage_sum = 0
        for p in reciever_list_in_group:
            percentage_sum += int(p.percentage)

        if percentage_sum != 100:
            return Response(
                {"message": "Sum of percentages should be equal to 100"},
                status=status.HTTP_412_PRECONDITION_FAILED,
            )

        for reciever in reciever_list_in_group:
            reciever_amount = initial_amount * (int(reciever.percentage) / 100)
            reciever.payment = reciever_amount

        transfer_list = []
        for a in reciever_list_in_group:
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
