from django.db import models


# Create your models here.
class Reciever(models.Model):
    bank_account = models.CharField(max_length=250, unique=True, primary_key=True)
    ifsc_code = models.CharField(max_length=20)
    email = models.EmailField(max_length=250, unique=True)
    phone = models.CharField(max_length=15)
    type = models.CharField(max_length=20)
    reference_id = models.CharField(max_length=20, unique=True)
    legal_business_name = models.CharField(max_length=250)
    business_type = models.CharField(max_length=250, default="partnership")
    contact_name = models.CharField(max_length=250)
    category = models.CharField(max_length=250)
    subcategory = models.CharField(max_length=250)
    street1 = models.CharField(max_length=250)
    street2 = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=250)
    payment = models.CharField(max_length=10, null=True, blank=True)
    percentage = models.CharField(max_length=4, null=True, blank=True)
    pan = models.CharField(max_length=100)
    gst = models.CharField(max_length=100)
    razor_id = models.CharField(max_length=100, null=True, blank=True)
