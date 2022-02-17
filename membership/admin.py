from django.contrib import admin

# Register your models here.
from .models import Membership, MpesaPayment, PaymentTransaction, UserMembership, Subscription, User

admin.site.register(User)

admin.site.register(Membership)
admin.site.register(UserMembership)
admin.site.register(Subscription)
admin.site.register(MpesaPayment)

admin.site.register(PaymentTransaction)
