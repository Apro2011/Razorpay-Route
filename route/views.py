from route.models import Reciever, RecieversGroup, Payment, TransactionHistory
from route.serializers import (
    RecieverSerializer,
    RecieverDetailsSerializer,
    RecieversGroupSerializer,
    PaymentSerializer,
    TransactionHistorySerializer,
)
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
from datetime import datetime
import pytz
import json
import requests
from core import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser


UTC = pytz.utc
IST = pytz.timezone("Asia/Kolkata")


# Create your views here.
class CreatingGroup(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, format=None):
        groups = RecieversGroup.objects.filter(created_by=request.user)

        serializer = RecieversGroupSerializer(groups, many=True)

        return Response(
            {"data": serializer.data, "status": True},
            status=status.HTTP_200_OK,
        )

    def post(self, request, format=None):
        serializer = RecieversGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data["created_by"] = request.user
            serializer.save()
            group = RecieversGroup.objects.get(
                name=serializer.validated_data.get("name")
            )
            group.photo = request.data.get("file")
            group.save()
            serializer.validated_data[
                "photo_url"
            ] = f'https://storage.googleapis.com/split-image-bucket/{request.data.get("file").name}'
            serializer.save()

            return Response(
                {
                    "data": serializer.data,
                    "status": True,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "data": serializer.errors,
                "status": False,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class GroupData(APIView):
    def put(self, request, pk, format=None):
        group = RecieversGroup.objects.get(pk=pk)
        recievers = Reciever.objects.filter(group_name=group.name)
        serializer1 = RecieversGroupSerializer(group)
        serializer2 = RecieverSerializer(recievers, many=True)

        return Response(
            {
                "group": serializer1.data,
                "related_recievers": serializer2.data,
                "status": True,
            },
            status=status.HTTP_200_OK,
        )


class RecieverList(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, format=None):
        recievers = Reciever.objects.filter(created_by=request.user)
        serializer = RecieverSerializer(recievers, many=True)

        return Response(
            {"data": serializer.data, "status": True},
            status=status.HTTP_200_OK,
        )

    def post(self, request, format=None):
        serializer = RecieverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data["created_by"] = request.user
            try:
                group = RecieversGroup.objects.get(
                    name=serializer.validated_data.get("group_name"),
                )
            except Exception as e:
                return Response({"error": f"{e}", "status": False})
            related_recievers = Reciever.objects.filter(group_name=group.name)

            percentage_sum = 0
            for p in related_recievers:
                if not p.percentage:
                    return Response({"errors": f"percentage of {p} is null"})
                percentage_sum += int(p.percentage)

            percentage_sum += int(serializer.validated_data.get("percentage"))

            if percentage_sum > 100:
                return Response(
                    {
                        "error": "Sum of percentages should be less than or equal to 100",
                        "status": False,
                    },
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )

            # Create Linked Accounts
            accounts_url = "https://api.razorpay.com/v2/accounts"
            account_data = {
                "email": serializer.validated_data.get("email"),
                "phone": serializer.validated_data.get("phone"),
                "type": serializer.validated_data.get("type", "route"),
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
                return Response(
                    {
                        "data": account_response.json(),
                        "status": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer.save()
                reciever = Reciever.objects.get(
                    reference_id=serializer.validated_data.get("reference_id")
                )
                reciever.group = group
                reciever.save()
                reciever.photo = request.data.get("file")
                reciever.save()
                serializer.validated_data[
                    "photo_url"
                ] = f'https://storage.googleapis.com/split-image-bucket/{request.data.get("file").name}'
                serializer.save()

                razor_id = json.loads(account_response.content.decode("utf-8"))["id"]
                serializer.validated_data["razor_id"] = razor_id
                serializer.save()
                stakeholder_url = (
                    "https://api.razorpay.com/v2/accounts/" + razor_id + "/stakeholders"
                )

                # Create Stakeholder account
                stakeholder_data = {
                    "name": serializer.validated_data["contact_name"],
                    "email": serializer.validated_data["email"],
                    "addresses": {
                        "residential": {
                            "street": serializer.validated_data["street1"],
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
                        {
                            "data": stakeholder_response.json(),
                            "status": False,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    product_config_url = (
                        "https://api.razorpay.com/v2/accounts/" + razor_id + "/products"
                    )

                    # Request Product Configuration
                    product_config_data = {
                        "product_name": serializer.validated_data.get(
                            "product_name", "route"
                        ),
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
                            {
                                "data": product_config_response.json(),
                                "status": False,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
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
                                    "legal_business_name"
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
                                {
                                    "data": update_product_config_response.json(),
                                    "status": False,
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        else:
                            return Response(
                                {
                                    "data": {
                                        "database_data": serializer.data,
                                        "razorpay_data": [
                                            account_response.json(),
                                            stakeholder_response.json(),
                                            product_config_response.json(),
                                            update_product_config_response.json(),
                                        ],
                                    },
                                    "status": True,
                                },
                                status=status.HTTP_201_CREATED,
                            )
        # pay_NHi3IhG1fg4qhK
        return Response(
            {
                "data": serializer.errors,
                "status": False,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class RecieverDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Reciever.objects.get(pk=pk)
        except Reciever.DoesNotExist:
            raise Http404

    def options(self, request, pk, format=None):
        reciever = self.get_object(pk=pk)
        serializer = RecieverSerializer(reciever)
        return Response(
            {
                "data": serializer.data,
                "status": True,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk, format=None):
        reciever = self.get_object(pk=pk)
        serializer = RecieverDetailsSerializer(
            reciever,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            # return Response({"error": f"{e}", "status": False})
            related_recievers = Reciever.objects.filter(group_name=reciever.group_name)

            percentage_sum = 0
            for p in related_recievers:
                if not p.percentage:
                    return Response({"errors": f"percentage of {p} is null"})
                percentage_sum += int(p.percentage)
            if serializer.validated_data.get("percentage") != None:
                percentage_sum += int(serializer.validated_data.get("percentage"))

            if percentage_sum > 100:
                return Response(
                    {
                        "error": "Sum of percentages should be less than or equal to 100",
                        "status": False,
                    },
                    status=status.HTTP_412_PRECONDITION_FAILED,
                )
            serializer.save()
            return Response(
                {
                    "data": serializer.data,
                    "status": True,
                },
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(
            {
                "data": serializer.errors,
                "status": False,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk, format=None):
        reciever = self.get_object(pk)
        try:
            reciever.delete()
        except Exception as e:
            return Response(
                {"message": "Deleted", "status": True},
                status=status.HTTP_204_NO_CONTENT,
            )


class UPIPaymentLinkAPIs(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        payments = Payment.objects.filter(created_by=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data["created_by"] = request.user

            # Create UPI Payment Link
            payment_url = "https://api.razorpay.com/v1/payment_links/"
            payment_data = {
                "upi_link": serializer.validated_data.get("upi_link"),
                "amount": int(serializer.validated_data.get("amount")) * 100,
                "currency": serializer.validated_data.get("currency"),
                "reference_id": serializer.validated_data.get("reference_id"),
                "description": serializer.validated_data.get("description"),
                "customer": {
                    "name": serializer.validated_data.get("customer_name"),
                    "contact": serializer.validated_data.get("customer_contact"),
                    "email": serializer.validated_data.get("email"),
                },
            }

            payment_response = requests.post(
                payment_url,
                auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
                headers={"Contact-Type": "application/json"},
                json=payment_data,
            )

            if payment_response.status_code != 200:
                return Response(
                    {
                        "data": payment_response.json(),
                        "status": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                try:
                    group = RecieversGroup.objects.get(
                        name=serializer.validated_data.get("group_name"),
                    )
                except Exception as e:
                    return Response({"error": f"{e}", "status": False})

                related_recievers = Reciever.objects.filter(group_name=group.name)
                initial_amount = int(serializer.validated_data.get("amount")) * 100
                for reciever in related_recievers:
                    reciever_amount = initial_amount * (int(reciever.percentage) / 100)
                    reciever.payment = str(int(reciever_amount))
                    reciever.save()

                serializer.save()

                payment_endpoint_data = json.loads(
                    payment_response.content.decode("utf-8")
                )
                serializer.validated_data["payment_link_id"] = payment_endpoint_data[
                    "id"
                ]
                if payment_endpoint_data["payments"] != None:
                    serializer.validated_data["paid_amount"] = payment_endpoint_data[
                        "payments"
                    ][0]["amount"]
                    serializer.validated_data[
                        "paid_payment_id"
                    ] = payment_endpoint_data["payments"][0]["payment_id"]
                    serializer.validated_data["paid_plink_id"] = payment_endpoint_data[
                        "payments"
                    ][0]["plink_id"]

                serializer.validated_data["short_url"] = payment_endpoint_data[
                    "short_url"
                ]
                serializer.validated_data["user_id"] = payment_endpoint_data["user_id"]
                serializer.save()

                return Response(
                    {
                        "data": [serializer.data, payment_response.json()],
                        "status": True,
                    },
                    status=status.HTTP_201_CREATED,
                )
        return Response(
            {
                "data": serializer.errors,
                "status": False,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UPIPaymentLinkData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        payment = Payment.objects.get(pk=pk)
        payment_url = (
            "https://api.razorpay.com/v1/payment_links/" + payment.payment_link_id
        )
        payment_response = requests.get(
            payment_url,
            auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
            headers={"Contact-Type": "application/json"},
        )

        if payment_response.status_code != 200:
            return Response(
                {
                    "data": payment_response.json(),
                    "status": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            payment_endpoint_data = json.loads(payment_response.content.decode("utf-8"))
            if payment_endpoint_data["payments"] != None:
                payment.paid_amount = payment_endpoint_data["payments"][0]["amount"]
                payment.paid_payment_id = payment_endpoint_data["payments"][0][
                    "payment_id"
                ]
                payment.save()
            serializer = PaymentSerializer(payment)

            return Response(
                {
                    "data": [serializer.data, payment_response.json()],
                    "status": True,
                },
                status=status.HTTP_200_OK,
            )

    def put(self, request, pk, format=None):
        payment = Payment.objects.get(pk=pk)
        serializer = PaymentSerializer(payment)
        return Response(
            {
                "data": serializer.data,
                "status": True,
            },
            status=status.HTTP_200_OK,
        )


class SplitPayments(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        payment_data = Payment.objects.get(pk=pk)
        reciever_list_in_group = Reciever.objects.filter(
            group_name=payment_data.group_name
        )

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

        payment_id = payment_data.paid_payment_id

        transfer_url = (
            "https://api.razorpay.com/v1/payments/" + payment_id + "/transfers"
        )

        transfer_data = {"transfers": transfer_list}

        transfer_response = requests.post(
            transfer_url,
            auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
            headers={"Contact-Type": "application/json"},
            json=transfer_data,
        )

        if transfer_response.status_code != 200:
            return Response(
                {
                    "data": transfer_response.json(),
                    "status": False,
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        group = RecieversGroup.objects.get(name=payment_data.group_name)
        group.paid_at = datetime.now(IST)
        group.save()

        for a in reciever_list_in_group:
            a.paid_at = group.paid_at
            a.save()

        payment_data.paid_at = group.paid_at
        payment_data.save()

        TransactionHistory.objects.create(
            paid_at=payment_data.paid_at,
            created_by=request.user,
            group=group,
            paid_amount=payment_data.paid_amount,
        )

        return Response(
            {
                "data": {
                    "payment_data": {"paid_at": payment_data.paid_at},
                    "razorpay_data": transfer_response.json(),
                },
                "status": True,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class TransactionHistoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        transactions = TransactionHistory.objects.filter(created_by=request.user)
        serializer = TransactionHistorySerializer(transactions, many=True)
        return Response(
            {"data": serializer.data, "status": True},
            status=status.HTTP_200_OK,
        )
