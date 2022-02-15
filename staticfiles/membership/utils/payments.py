import json
import logging
from base64 import b64encode
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
import secrets
from ..mpesa_credentials import LipanaMpesaPpassword, MpesaC2bCredential

# consumer_key = MpesaC2bCredential.consumer_key
# consumer_secret = MpesaC2bCredential.consumer_secret
# api_url = MpesaC2bCredential.api_URL


def authenticate():
    """
    :return: MPESA_TOKEN
    """

    consumer_key = MpesaC2bCredential.consumer_key
    consumer_secret = MpesaC2bCredential.consumer_secret
    api_url = MpesaC2bCredential.api_URL_token
    r = requests.get(api_url,
                     auth=HTTPBasicAuth(consumer_key, consumer_secret))
    print(r.text)
    return r.text


def stk_push(amount, phonenumber, callbackurl):

    business_shortcode = LipanaMpesaPpassword.Business_short_code
    lipa_na_mpesapasskey = LipanaMpesaPpassword.passkey
    party_a = LipanaMpesaPpassword.Business_short_code
    token_data = authenticate()
    try:
        token = json.loads(token_data)["access_token"]
    except Exception:
        token = ""
    api_url = MpesaC2bCredential.api_URL
    headers = {"Authorization": "Bearer %s" % token}
    timestamp = datetime.now().strftime("%Y%m%d%I%M%S")
    pswd = (business_shortcode + lipa_na_mpesapasskey +
            timestamp).encode("utf-8")
    password = b64encode(pswd).decode()
    req = {
        "BusinessShortCode": business_shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": party_a,
        "PartyB": business_shortcode,
        "PhoneNumber": phonenumber,
        "CallBackURL": callbackurl,
        "AccountReference": business_shortcode,
        "TransactionDesc": secrets.token_hex(),
    }
    response = requests.post(api_url, json=req, headers=headers)

    # logging.info("response", response)
    return response