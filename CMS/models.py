from django.db import models

class Name(models.Model):
    full_names = models.TextField(default=list,blank=False,null=False)

    def __str__(self):
        return f"{self.full_names}"

class Email(models.Model):
    primary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.primary

class PhoneNumber(models.Model):
    primary = models.TextField(null=False,blank=False)

    def __str__(self):
        return self.primary

class Address(models.Model):
    complete_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True,null=True)
    state = models.TextField(blank=True,null=True)
    pincode = models.TextField(blank=True,null=True)
    landmark = models.TextField(blank=True,null=True)

    def __str__(self):
        return f"{self.complete_address}, {self.city}, {self.state}"

class PlotDimensions(models.Model):
    plotEast = models.TextField(default="0",blank=True,null=True)
    plotWest = models.TextField(default="0",blank=True,null=True)
    plotNorth = models.TextField(default="0",blank=True,null=True)
    plotSouth = models.TextField(default="0",blank=True,null=True)

class PlotDetails(models.Model):
    plot_number = models.TextField(default="0",null=True,blank=True)
    plot_area = models.TextField(blank=True, null=True)
    plot_dimensions = models.OneToOneField(PlotDimensions,on_delete=models.CASCADE)
    roadDirection = models.CharField(max_length=30,null=True , blank=True)
    roadWidth = models.CharField(max_length=10,null=True,blank=True)



class ClientRequirements(models.Model):
    requirements = models.TextField(null=True,blank=True)


    def __str__(self):
        return str(self.requirements)


class Services(models.Model):
    services = models.JSONField(default = dict,null=True,blank=True)
    details = models.JSONField(default = dict,null=True,blank=True)


class PaymentDetails(models.Model):
    transactions = models.JSONField(default=list)
    advancedPayment = models.FloatField(default=0)
    original_amount = models.FloatField(default=0)
    total_amount_paid = models.FloatField(default=0)
    total_amount_due = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0)
    totalPayableAmount = models.FloatField(default=0)

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    is_project_pending = models.BooleanField(default=True)
    is_payment_pending = models.BooleanField(default=True)
    name = models.OneToOneField(Name, on_delete=models.CASCADE)
    referred_by = models.CharField(max_length=255, blank=True, null=True, default="Self")
    email = models.OneToOneField(Email, on_delete=models.CASCADE)
    phone_number = models.OneToOneField(PhoneNumber, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    plot_details = models.OneToOneField(PlotDetails, on_delete=models.CASCADE)
    image_link = models.URLField(default=None,null=True,blank=True)
    client_requirements = models.OneToOneField(ClientRequirements, on_delete=models.CASCADE)
    services = models.OneToOneField(Services, on_delete=models.CASCADE)
    total_bill = models.IntegerField(default=0,null=False,blank=True)
    payment_details = models.OneToOneField(PaymentDetails, on_delete=models.CASCADE)
    date_of_registration = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    specialNotes = models.TextField(blank=True,null=True)

    def __str__(self):
        return f"Customer: {self.name.full_names}"