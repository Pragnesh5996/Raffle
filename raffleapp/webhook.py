import requests
import json
import hashlib
import base64
from .models import installer, uninstall_data
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import hmac
import datetime
import os
from decouple import config

API_KEY = config('API_KEY')
SHARED_SECRET = config('SHARED_SECRET')
API_VERSION = config('API_VERSION')


# encrypt data functional start (uninstall app then save the uninstall time data in encrypted format)  #
def encrypt(data_json):
    data2 = json.dumps(data_json)
    sample_string_bytes = data2.encode("ascii") 
    base64_bytes = base64.b64encode(sample_string_bytes)
    return base64_bytes.decode('utf-8')
# encrypt data functional end #

class WebhookApi(object):
    # shopify Uninstalling app webhook  functional code start #
    @csrf_exempt
    def webhook_uninstall(request):
        if request.method == 'POST':        # check that the request method is POST or not #
            print(API_KEY, SHARED_SECRET, API_VERSION)
            if ((request.body != "") and (request.headers.get('X-Shopify-Hmac-Sha256') != "")):     # check 'request.body' and  'request.headers.get('X-Shopify-Hmac-Sha256')' is not blank #
                data = request.body
                tkn = ''
                shop_url = ''
                hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
                digest = hmac.new(SHARED_SECRET.encode('utf-8'), data, hashlib.sha256).digest() # create new hmac from gethered data (data, hashlib.sha256 and shared_secret) #
                computed_hmac = base64.b64encode(digest)    # encoded hmac that create above #

                if computed_hmac == hmac_header.encode('utf-8'):    # match hmac_header and computed_hmac then get the topic and shop_url #
                    topic = request.headers.get('X-Shopify-Topic')
                    shop_url = request.headers.get('X-Shopify-Shop-Domain')
                    if shop_url != "":      # check the 'shop_url' is not blank #
                        uninstallap = installer.objects.filter(shop=str(shop_url))  # 'installer' table data filter by 'shop_url' #
                        if uninstallap: # get the record then #
                            tkn = uninstallap[0].access_token
                            encrypt_data = encrypt(data_json=data.decode('utf-8'))      # encrypt the data that gether while UninstallApp #
                            date = datetime.datetime.now()
                            
                            # start call 'uninstall_data' table and store the data to it #
                            data = uninstall_data()     
                            data.uninstall_shop = uninstallap[0].shop
                            data.uninstall_time = date
                            data.uninstall_log = encrypt_data
                            data.save()
                            # end save data in uninstall_data #
                            uninstallap.delete()            # delete record from 'installer' table while 'shop_url' is match in data #    
                    else:
                        return HttpResponse("NO shop domain")
                else:
                    return HttpResponse("FALSE")
        return HttpResponse('Success')
        # shopify Uninstalling app webhook  functional code end #
    