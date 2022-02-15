from django.urls import path

from .views import (MembershipSelectView, PaymentView, call_back,
                    cancelSubscription, confirmation, loginPage, logoutUser,
                    profile_view, register_urls, registerPage,
                    updateTransactionRecords, validation)

app_name = 'memberships'

urlpatterns = [
    path('', MembershipSelectView.as_view(), name='select'),
    path('payment/', PaymentView, name='payment'),
    path('update-transactions/<subscription_id>/',
         updateTransactionRecords,
         name='update-transactions'),
    path('logout/', logoutUser, name='logout'),
    path('login/', loginPage, name='login'),
    path('signup/', registerPage, name='signup'),
    path('profile/', profile_view, name='profile'),
    path('cancel/', cancelSubscription, name='cancel'),
    path('c2b/register', register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', confirmation, name="confirmation"),
    path('c2b/validation', validation, name="validation"),
    path('c2b/callback', call_back, name="call_back"),
]