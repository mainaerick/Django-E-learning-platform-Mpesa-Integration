import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import os
from django.conf import settings
from dotenv import dotenv_values
config = dotenv_values(".env")

class MpesaC2bCredential:
    # live
    
    consumer_key = config['consumer_key']
    consumer_secret = config['consumer_secret']
    api_URL = config['api_URL']
    api_URL_token = config['api_URL_token']
    callbackUrl = config['callbackUrl']
    
    # test
    # consumer_key = "qq4lh4XeRQDGKVnvJS4OyGYL2xFtJT2s"
    # consumer_secret = "GdWPdMXMWKVMu7Xm"
    # api_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  #test
    # api_URL_token = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"


class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = config['Business_short_code']
    passkey = config['passkey']

    # passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    # Business_short_code = "174379"
    print(Business_short_code)
    data_to_encode = Business_short_code + passkey + lipa_time

    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
