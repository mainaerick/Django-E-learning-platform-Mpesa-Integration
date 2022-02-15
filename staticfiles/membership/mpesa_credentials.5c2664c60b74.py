import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64


class MpesaC2bCredential:
    # live
    consumer_key = "kAXqU8JZzdzxUchRKnnaKVPX5AVl1MLZ"
    consumer_secret = "Dmpu7oYaCULD1xZG"
    api_URL = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  #live
    api_URL_token = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # test
    # consumer_key = "qq4lh4XeRQDGKVnvJS4OyGYL2xFtJT2s"
    # consumer_secret = "GdWPdMXMWKVMu7Xm"
    # api_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  #test
    # api_URL_token = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"


class LipanaMpesaPpassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "4029829"
    passkey = '2ce084c9f634b1334c806ce7c7b3cbfdf8f6a5e5b1a4a94f64a5495a3cb27960'
    # passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    # Business_short_code = "174379"
    data_to_encode = Business_short_code + passkey + lipa_time

    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
