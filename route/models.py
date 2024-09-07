from django.db import models
from sender_auth_app.models import Sender


# Create your models here.
class RecieversGroup(models.Model):
    paid_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        Sender, on_delete=models.PROTECT, null=True, blank=True
    )
    name = models.CharField(max_length=200, unique=True)
    photo = models.ImageField(upload_to="", null=True, blank=True)
    photo_url = models.CharField(max_length=5000, null=True, blank=True)
    total_amount = models.CharField(max_length=10, null=True, blank=True)


class Reciever(models.Model):
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_status = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        Sender, on_delete=models.PROTECT, null=True, blank=True
    )
    main_id = models.BigAutoField(unique=True, primary_key=True)
    email = models.EmailField(max_length=250)
    legal_business_name = models.CharField(max_length=250)
    business_type = models.CharField(max_length=250, default="individual")
    contact_name = models.CharField(max_length=250, null=True, blank=True)
    payment = models.CharField(max_length=10, null=True, blank=True)
    percentage = models.CharField(max_length=4, default="0")
    razor_id = models.CharField(max_length=100, null=True, blank=True)
    group_name = models.CharField(max_length=100, null=True, blank=True)
    tnc_accepted = models.BooleanField(default=True)
    account_number = models.CharField(max_length=250, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)

    # Add related_name to resolve reverse accessor clash
    group = models.ForeignKey(
        RecieversGroup,
        related_name="reciever_recieversgroup",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    photo = models.ImageField(upload_to="", null=True, blank=True)
    photo_url = models.CharField(max_length=5000, null=True, blank=True)


class Payment(models.Model):
    paid_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        Sender, on_delete=models.PROTECT, null=True, blank=True
    )
    upi_link = models.BooleanField(default=True)
    amount = models.IntegerField()
    currency = models.CharField(max_length=10, default="INR")
    reference_id = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_contact = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=250, null=True, blank=True)
    callback_url = models.URLField(max_length=200, null=True, blank=True)
    callback_method = models.CharField(max_length=200, default="get")
    payment_link_id = models.CharField(max_length=200, null=True, blank=True)
    paid_amount = models.CharField(max_length=100, null=True, blank=True)
    paid_payment_id = models.CharField(max_length=200, null=True, blank=True)
    paid_plink_id = models.CharField(max_length=200, null=True, blank=True)
    short_url = models.URLField(max_length=200, null=True, blank=True)
    user_id = models.CharField(max_length=200, null=True, blank=True)
    group_name = models.CharField(max_length=100, null=True, blank=True)


class TransactionHistory(models.Model):
    paid_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        Sender, on_delete=models.PROTECT, null=True, blank=True
    )
    group = models.ForeignKey(
        RecieversGroup,
        related_name="transaction_history_recieversgroup",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    paid_amount = models.CharField(max_length=100, null=True, blank=True)
