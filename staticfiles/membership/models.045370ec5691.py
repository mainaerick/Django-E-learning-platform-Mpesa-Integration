from datetime import datetime
from venv import create
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
MEMBERSHIP_CHOICES = (('Enterprise', 'ent'), ('Professional', 'pro'), ('Free',
                                                                       'free'))


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    phone_regex = RegexValidator(
        regex=r"^(254)([7][0-9]|[1][0-1]){1}[0-9]{1}[0-9]{6}$",
        message=
        "Phone number must be entered in the format: '254712345678. Up to 12 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex],
                             unique=True,
                             max_length=12,
                             blank=True)  # validators should be a list
    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']


class Membership(models.Model):
    slug = models.SlugField()
    membership_type = models.CharField(choices=MEMBERSHIP_CHOICES,
                                       default='Free',
                                       max_length=30)
    price = models.IntegerField(default=15)
    mpesa_plan_id = models.CharField(max_length=40)

    def __str__(self):
        return self.membership_type


class UserMembership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mpesa_customer_id = models.CharField(max_length=40)
    membership = models.ForeignKey(Membership,
                                   on_delete=models.SET_NULL,
                                   null=True)

    def __str__(self):
        return self.user.username


def post_save_usermembership_create(sender, instance, created, *args,
                                    **kwargs):
    if (created):
        UserMembership.objects.get_or_create(user=instance)

    user_membership, created = UserMembership.objects.get_or_create(
        user=instance)

    if user_membership.mpesa_customer_id is None or user_membership.mpesa_customer_id == '':
        new_customer_id = instance.phone
        # free_membership = Membership.objects.get(membership_type='Free')
        user_membership.mpesa_customer_id = new_customer_id
        # user_membership.membership = free_membership
        user_membership.save()


post_save.connect(post_save_usermembership_create, sender=User)


class Subscription(models.Model):
    user_membership = models.ForeignKey(UserMembership,
                                        on_delete=models.CASCADE)
    mpesa_subscription_id = models.CharField(max_length=40)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_membership.user.username

    @property
    def get_created_date(self):
        subscription = stripe.Subscription.retrieve(
            self.stripe_subscription_id)
        return datetime.fromtimestamp(subscription.created)

    @property
    def get_next_billing_date(self):
        subscription = stripe.Subscription.retrieve(
            self.stripe_subscription_id)
        return datetime.fromtimestamp(subscription.current_period_end)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# M-pesa Payment models


class MpesaCalls(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call'
        verbose_name_plural = 'Mpesa Calls'


class MpesaCallBacks(BaseModel):
    ip_address = models.TextField()
    caller = models.TextField()
    conversation_id = models.TextField()
    content = models.TextField()

    class Meta:
        verbose_name = 'Mpesa Call Back'
        verbose_name_plural = 'Mpesa Call Backs'


class MpesaPayment(BaseModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    type = models.TextField()
    reference = models.TextField()
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.TextField()
    organization_balance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Mpesa Payment'
        verbose_name_plural = 'Mpesa Payments'

    def __str__(self):
        return self.first_name