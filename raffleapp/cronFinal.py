from .models import Product_Raffle, installer, Raffle, Subscribers
from .email import SendWinnerEmail, SendLoserEmail, SendVendorEmail
from django.http import HttpResponse
from datetime import datetime
from .Apis import Required_api

def Select(request):
    if request.method == "GET":
        quntity = ''
        token = ''
        shop = ''
        vendor_email = ''
        store_id = ''

        check_raffle = Raffle.objects.filter(is_active=True, is_deleted=False, is_new=True)

        subscriber_dict = dict()
        subscriber_list = list()
        loser_subscriber_list = list()
        winner_subscriber_list = list()
        i = 1

        for x in check_raffle:
            if (x.end_date.strftime("%Y-%m-%d %H:%M") == datetime.now().strftime("%Y-%m-%d %H:%M")):
                Raffle.objects.filter(id=x.id).update(is_active=False, is_new=False)

                check_installer = installer.objects.filter(id=x.installer_id_id)
                if check_installer:
                    token = check_installer[0].access_token
                    shop = check_installer[0].shop
                
                vendor_email, store_id = Required_api.get_vendor_email(shop=shop, token=token)

                check_raffale_variant = Product_Raffle.objects.filter(Raffle_id_id=x.id, is_deleted=False)
                if check_raffale_variant:
                    get_quntity = Required_api.get_variant_quantity(varid=check_raffale_variant[0].variant_id, shop=shop, token=token)
                    if get_quntity:
                        quntity = get_quntity
                    
                    if x.is_automatic == True: # for automatic #
                        check_subscribers = Subscribers.objects.filter(product_raffle_id_id=check_raffale_variant[0].id, is_active=True, is_deleted=False, is_winner=None)
                        if check_subscribers:
                            for y in check_subscribers:
                                subscriber_list.append(y.customerid)

                        import secrets
                        while i <= quntity:
                            Winner = secrets.choice(subscriber_list)
                            Subscribers.objects.filter(customerid=Winner, product_raffle_id_id=check_raffale_variant[0].id, is_active=True, is_deleted=False, is_winner=None).update(is_winner=True)
                            subscriber_data = Required_api.get_subscriber(subscriber_id=Winner, shop=shop, token=token)
                            address = subscriber_data['customer']['default_address']
                            email = subscriber_data['customer']['email']
                            phone = subscriber_data['customer']['phone']
                            create_order = Required_api.create_pending_order(shop=shop, token=token, address=address, variant=check_raffale_variant[0].variant_id, email=email, phone=phone, subscriber=Winner)
                            order_id = create_order['order']['id']
                            user_email = create_order['order']['email']
                            order_status_url = create_order['order']['order_status_url']
                            key = order_status_url.split('?key=')[1] 
                            payment_url = "https://%s/%s/order_payment/%s?secret=%s" % (shop, store_id, order_id, key)
                            SendWinnerEmail(subscriber_email=user_email, product_id=check_raffale_variant[0].product_id, variant_id=check_raffale_variant[0].variant_id, raffle_id=x.id, shop=shop, token=token, url=payment_url)
                            winner_subscriber_list.append(Winner)
                            i += 1
                        
                        for z in subscriber_list:
                            if z not in winner_subscriber_list:
                                subscriber_data = Required_api.get_subscriber(subscriber_id=z, shop=shop, token=token)
                                SendLoserEmail(subscriber_email=subscriber_data['customer']['email'], product_id=check_raffale_variant[0].product_id, variant_id=check_raffale_variant[0].variant_id, raffle_id=x.id, shop=shop, token=token)
                                Subscribers.objects.filter(customerid=z, product_raffle_id_id=check_raffale_variant[0].id, is_active=True, is_deleted=False, is_winner=None).update(is_winner=False)
                                loser_subscriber_list.append(z)      
                    else: # for menual #
                        url = "https://raffle.pagekite.me/SelectWinnerManually?raffle_id=%s&quntity=%s" % (x.id, quntity)
                        s = SendVendorEmail(url=url, vendor_email='pragnesh2612raval@gmail.com')
                        if s == "Account successfully created":
                            pass
                        else:
                            return HttpResponse('no')
        return HttpResponse('hello')