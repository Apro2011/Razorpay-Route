from django.db import models


# Create your models here.
class RecieversGroup(models.Model):
    name = models.CharField(max_length=200)


class Reciever(models.Model):
    main_id = models.BigAutoField(unique=True, primary_key=True)
    email = models.EmailField(max_length=250, unique=True)
    phone = models.CharField(max_length=15)
    type = models.CharField(max_length=20)
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
    tnc_accepted = models.BooleanField(default=False)
    product_id = models.CharField(max_length=100, null=True, blank=True)
    product_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=250, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)

    # Add related_name to resolve reverse accessor clash
    groups = models.ManyToManyField(
        RecieversGroup, related_name="reciever_recievergroups", blank=True
    )
