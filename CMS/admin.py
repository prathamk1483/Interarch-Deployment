from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Name)
admin.site.register(Email)
admin.site.register(PhoneNumber)
admin.site.register(Address)
admin.site.register(PlotDetails)
admin.site.register(ClientRequirements)
admin.site.register(Services)
admin.site.register(PaymentDetails)
admin.site.register(PlotDimensions)