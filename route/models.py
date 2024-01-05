from django.db import models
from sender_auth_app.models import Sender


# Create your models here.
class RecieversGroup(models.Model):
    created_by = models.ForeignKey(
        Sender, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=200, unique=True)
    photo = models.ImageField(upload_to="", null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True, max_length=50000)


class Reciever(models.Model):
    created_by = models.ForeignKey(
        Sender, on_delete=models.CASCADE, null=True, blank=True
    )
    main_id = models.BigAutoField(unique=True, primary_key=True)
    email = models.EmailField(max_length=250, unique=True)
    phone = models.CharField(max_length=15)
    type = models.CharField(max_length=20, default="route")
    reference_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    legal_business_name = models.CharField(max_length=250)
    business_type = models.CharField(max_length=250, default="individual")
    contact_name = models.CharField(max_length=250, null=True, blank=True)
    category = models.CharField(max_length=250, null=True, blank=True)
    subcategory = models.CharField(max_length=250, null=True, blank=True)
    street1 = models.CharField(max_length=250, null=True, blank=True)
    street2 = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    state = models.CharField(max_length=250, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=250, null=True, blank=True)
    payment = models.CharField(max_length=10, null=True, blank=True)
    percentage = models.CharField(max_length=4, null=True, blank=True)
    pan = models.CharField(max_length=100, null=True, blank=True)
    gst = models.CharField(max_length=100, null=True, blank=True)
    razor_id = models.CharField(max_length=100, null=True, blank=True)
    group_name = models.CharField(max_length=100, null=True, blank=True)
    tnc_accepted = models.BooleanField(default=True)
    product_id = models.CharField(max_length=100, null=True, blank=True)
    product_name = models.CharField(max_length=100, default="route")
    account_number = models.CharField(max_length=250, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)

    # Add related_name to resolve reverse accessor clash
    groups = models.ManyToManyField(
        RecieversGroup, related_name="reciever_recievergroups", blank=True
    )
    photo = models.ImageField(upload_to="", null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True, max_length=50000)


class Payment(models.Model):
    created_by = models.ForeignKey(
        Sender, on_delete=models.CASCADE, null=True, blank=True
    )
    upi_link = models.BooleanField(default=True)
    amount = models.IntegerField()
    currency = models.CharField(max_length=10, default="INR")
    reference_id = models.CharField(max_length=100, unique=True)
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
