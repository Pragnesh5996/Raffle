from django.http import HttpResponse, JsonResponse
from .models import installer, Raffle, Product_Raffle, Subscribers
from decouple import config
import requests
import json
from .Apis import Required_api

API_KEY = config('API_KEY')
SHARED_SECRET = config('SHARED_SECRET')
API_VERSION = config('API_VERSION')

def get_raffle_detail(request):
    if request.method == "GET":
        token = ''
        subscriber_raffle = dict()
        subscriber_raffle_list = list()

        if (request.GET.get('customer') is not None and request.GET.get('customer') != '' and request.GET.get('shopdata') is not None and request.GET.get('shopdata') != ''):
            check_installer = installer.objects.filter(shop=request.GET.get('shopdata'))
            if check_installer:
                token = check_installer[0].access_token
                check_subscriber = Subscribers.objects.filter(customerid=request.GET.get('customer'), is_active=True, is_deleted=False)
                if check_subscriber:
                    for x in check_subscriber:
                        check_raffle_product = Product_Raffle.objects.filter(id=x.product_raffle_id_id, is_deleted=False)
                        if check_raffle_product:
                            product_title =  Required_api.get_product_title(product_id=check_raffle_product[0].product_id, shop=request.GET.get('shopdata'), token=token)
                            variant_title = Required_api.get_variant_title(variant_id=check_raffle_product[0].variant_id, shop=request.GET.get('shopdata'), token=token)
                            sub_raffle_dict = {
                                'product_title':product_title,
                                'variant_title':variant_title,
                                'subscribed_at':str(x.createddate),
                                'status':x.is_winner
                            }
                            subscriber_raffle_list.append(sub_raffle_dict)
                else:
                    subscriber_raffle['error'] = 'Invalid Subscriber'
                    return HttpResponse(json.dumps(subscriber_raffle), content_type="application/json")
            else:
                subscriber_raffle['error'] = 'Invalid Store Detail'
                return HttpResponse(json.dumps(subscriber_raffle), content_type="application/json")
        else:
            subscriber_raffle['error'] = 'Some fields are missing'
            return HttpResponse(json.dumps(subscriber_raffle), content_type="application/json")
        
        subscriber_raffle['raffle'] = subscriber_raffle_list
        return HttpResponse(json.dumps(subscriber_raffle), content_type="application/json")
