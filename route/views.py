from route.models import Reciever
from route.serializers import RecieverSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
import json
import requests
from core import settings


# Create your views here.
class RecieverList(APIView):
    def get(self, request, format=None):
        recievers = Reciever.objects.all()
        serializer = RecieverSerializer(recievers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RecieverSerializer(data=request.data)
        if serializer.is_valid():
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

            # razor_id = json.loads(account_response.content.decode("utf-8"))["id"]
            # serializer.validated_data["razor_id"] = razor_id
            # serializer.save()

            return Response(account_response.json(), status=status.HTTP_201_CREATED)
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
