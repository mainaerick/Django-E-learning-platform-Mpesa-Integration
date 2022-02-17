from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.urls import reverse

from .forms import MyUserCreationForm

from .models import Membership, MpesaPayment, PaymentTransaction, User, UserMembership, Subscription
from .utils import payments
from requests.auth import HTTPBasicAuth
import json
import requests

from .mpesa_credentials import LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout


def loginPage(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect('course:home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('course:home')
        else:
            messages.error(request, "Username or Password does not exist")
    context = {"page": page}

    return render(request, 'membership/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('memberships:login')


def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()
    if request.user.is_authenticated:
        return redirect('course:home')
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            # commit freezes saving,checks if user exist
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('course:home')
        else:
            messages.error(request, "An error occured during registration")
    else:
        messages.error(request, "An error occured during registration")

    context = {"page": page, "form": form}
    return render(request, 'membership/login_register.html', context)


def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None


def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(
        user_membership=get_user_membership(request))
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None


def get_selected_membership(request):
    membership_type = request.session['selected_membership_type']
    selected_membership_qs = Membership.objects.filter(
        membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None


@login_required
def profile_view(request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    context = {
        'user_membership': user_membership,
        'user_subscription': user_subscription
    }
    return render(request, "membership/profile.html", context)


class MembershipSelectView(LoginRequiredMixin, ListView):
    login_url = '/membership/login/'
    model = Membership

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context

    def post(self, request, **kwargs):
        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)
        selected_membership_type = request.POST.get('membership_type')

        selected_membership = Membership.objects.get(
            membership_type=selected_membership_type)

        if user_membership.membership == selected_membership:
            if user_subscription is not None:
                messages.info(
                    request, """You already have this membership. Your
                              next payment is due {}""".format(
                        'get this value from stripe'))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # assign to the session
        request.session[
            'selected_membership_type'] = selected_membership.membership_type

        return HttpResponseRedirect(reverse('memberships:payment'))


@login_required
def PaymentView(request):
    user_membership = get_user_membership(request)
    try:
        selected_membership = get_selected_membership(request)
    except:
        return redirect(reverse("memberships:select"))
    publishKey = settings.MEDIA_URL
    if request.method == 'POST':
        # phonenumber = request.user.phone
        phonenumber = request.POST.get('phonenumber')
        if phonenumber:
            print("hello")
        else:
            phonenumber = request.user.phone
        callback_url = f"https://ecourseapp.herokuapp.com/membership/c2b/confirmation"
        stk_response = payments.stk_push(1, phonenumber, callback_url)
        print(stk_response)
        # if stk_response.status_code < 299:
        #     messages.success(request,
        #                      "request has being made to " + phonenumber)

        transaction_id = None
        # json_response = json.loads(stk_response)
        if "ResponseCode" in stk_response:
            if stk_response["ResponseCode"] == "0":

                checkout_id = stk_response["CheckoutRequestID"]
                if transaction_id:

                    transaction = PaymentTransaction.objects.filter(
                        id=transaction_id)
                    transaction.checkout_request_id = checkout_id
                    transaction.save()
                    return transaction.id
                else:
                    transaction = PaymentTransaction.objects.create(phone_number=phonenumber,
                                                                    checkout_request_id=checkout_id,
                                                                    amount=1.00, order_id=0)

                    transaction.save()
                    print(transaction)
                    # return transaction.id
        # else:
        #     raise Exception("Error sending MPesa stk push", stk_response)

    context = {
        'publishKey': publishKey,
        'selected_membership': selected_membership
    }
    return render(request, "membership/membership_payment.html", context)


@login_required
def updateTransactionRecords(request, subscription_id):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)
    user_membership.membership = selected_membership
    user_membership.save()

    sub, created = Subscription.objects.get_or_create(
        user_membership=user_membership)
    sub.mpesa_subscription_id = subscription_id
    sub.active = True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except:
        pass

    messages.info(
        request,
        'Successfully created {} membership'.format(selected_membership))
    return redirect(reverse('memberships:select'))


@login_required
def cancelSubscription(request):
    user_sub = get_user_subscription(request)

    if user_sub.active is False:
        messages.info(request, "You dont have an active membership")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    sub = stripe.Subscription.retrieve(user_sub.stripe_subscription_id)
    sub.delete()

    user_sub.active = False
    user_sub.save()

    free_membership = Membership.objects.get(membership_type='Free')
    user_membership = get_user_membership(request)
    user_membership.membership = free_membership
    user_membership.save()

    messages.info(request,
                  "Successfully cancelled membership. We have sent an email")
    # sending an email here

    return redirect(reverse('memberships:select'))


@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):

    context = {"ResultCode": 0, "ResultDesc": "Accepted"}
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    return HttpResponseRedirect(request.path_info)
    mpesa_body = request.body.decode('utf-8')
    request_data = json.loads(mpesa_body)
    print(request_data)
    body = request_data.get('Body')
    resultcode = body.get('stkCallback').get('ResultCode')
    # Perform your processing here e.g. print it out...
    if resultcode == 0:
        print('Payment successful')
        requestId = body.get('stkCallback').get('CheckoutRequestID')
        metadata = body.get('stkCallback').get(
            'CallbackMetadata').get('Item')
        for data in metadata:
            if data.get('Name') == "MpesaReceiptNumber":
                receipt_number = data.get('Value')
        transaction = PaymentTransaction.objects.get(
            checkout_request_id=requestId)
        if transaction:
            transaction.trans_id = receipt_number
            transaction.is_finished = True
            transaction.is_successful = True
            transaction.save()
            print(" haha")
        return redirect(reverse('memberships:update-transactions',
                                kwargs={
                                    'subscription_id': receipt_number
                                }))

    else:
        print('unsuccessfull')
        requestId = body.get('stkCallback').get('CheckoutRequestID')
        transaction = PaymentTransaction.objects.get(
            checkout_request_id=requestId)
        if transaction:
            transaction.is_finished = True
            transaction.is_successful = False
            transaction.save()

        # Prepare the response, assuming no errors have occurred. Any response
        # other than a 0 (zero) for the 'ResultCode' during Validation only means
        # an error occurred and the transaction is cancelled
    message = {
        "ResultCode": 0,
        "ResultDesc": "The service was accepted successfully",
        "ThirdPartyTransID": "1237867865"
    }

    # Send the response back to the server
    context = {"ResultCode": 0, "ResultDesc": "Accepted"}

    return JsonResponse(dict(context))


@csrf_exempt
def register_urls(request):
    token_data = payments.authenticate()
    try:
        access_token = json.loads(token_data)["access_token"]
    except Exception:
        access_token = ""
    # access_token = MpesaAccessToken.validated_mpesa_access_token
    print(access_token)

    # live
    api_url = "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    # test
    # api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"

    headers = {"Authorization": "Bearer %s" % access_token}
    options = {
        "ShortCode":
        LipanaMpesaPpassword.Business_short_code,
        "ResponseType":
        "Completed",
        "ConfirmationURL":
        "https://5d47-102-166-208-156.ngrok.io/membership/c2b/confirmation",
        "ValidationURL":
        "http://5d47-102-166-208-156.ngrok.io/membership/c2b/validation"
    }
    response = requests.post(api_url, json=options, headers=headers)

    return HttpResponse(response.text)
