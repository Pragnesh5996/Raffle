from django.db import models
from django.db.models import Q
from datetime import datetime
# from ckeditor.fields import RichTextField


# Create your models here.
class installer(models.Model):  # installer table #
    hmac = models.CharField(max_length=2000)
    shop = models.CharField(max_length=2000)
    code = models.CharField(max_length=2000)
    access_token = models.CharField(max_length=2000)
    install_date = models.DateTimeField(default=datetime.now())


class uninstall_data(models.Model):     # uninstall_data table #
    uninstall_shop = models.CharField(max_length=500)
    uninstall_time = models.CharField(max_length=200)
    uninstall_log = models.CharField(max_length=3000)

class Raffle(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    content = models.CharField(max_length=5000)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_new = models.BooleanField(blank=True, null=True, default="")
    installer_id = models.ForeignKey(installer, on_delete=models.CASCADE)
    is_automatic = models.BooleanField()

class Product_Raffle(models.Model):
    product_id = models.IntegerField()
    variant_id = models.IntegerField()
    Raffle_id = models.ForeignKey(Raffle, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)


class Subscribers(models.Model):
    product_raffle_id = models.ForeignKey(Product_Raffle, on_delete=models.CASCADE)
    customerid = models.IntegerField()
    createddate = models.DateTimeField(default=datetime.now())
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_winner = models.BooleanField(blank=True, null=True, default="")

class WinnderEmail(models.Model):
    winnertemplate = models.CharField(max_length=5000)
    installer_id = models.ForeignKey(installer, on_delete=models.CASCADE)
    Raffle_id = models.ForeignKey(Raffle, on_delete=models.CASCADE)

class LoserEmail(models.Model):
    losertemplate = models.CharField(max_length=5000)
    installer_id = models.ForeignKey(installer, on_delete=models.CASCADE)
    Raffle_id = models.ForeignKey(Raffle, on_delete=models.CASCADE)
