from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt
import requests
from datetime import datetime
import shopify as shopifyapi
from .models import installer, Raffle, Product_Raffle, Subscribers, WinnderEmail, LoserEmail
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from django.db.models import Q
from django.shortcuts import redirect as redc
from decouple import config
from django.contrib import messages
from .Apis import Required_api
from .email import SendWinnerEmail, SendLoserEmail
# from .forms import WinnerForm

API_KEY = config('API_KEY')
SHARED_SECRET = config('SHARED_SECRET')
API_VERSION = config('API_VERSION')

shop = ""
get_tkn = ""

# login page view functional code start (display template while go to main page) #
def login(request):
    return render(request, 'login.html')
# login page view functional code end #

# generate token functional code start #
def token(code, shop):
    ''' GENERATE ACCESS_TOKEN '''
    ur = "https://" + shop + "/admin/oauth/access_token"

    s = {
        "client_id": API_KEY,
        "client_secret": SHARED_SECRET,
        "code": code
    }
    r = requests.post(url=ur, json=s)
    x = json.loads(r.text)
    return x
# generate token functional code end #

# installation process functional code start #
def installation(request):
    if request.method == "POST":        # check request is post #
        url = request.POST['shop']      
        s_url = url.strip('/')
    
        api_key = API_KEY
        
        link = '%s/admin/oauth/authorize?client_id=%s&redirect_uri=https://raffle.pagekite.me/final&scope=read_products,read_inventory,write_products,read_customers,write_customers,read_orders,write_orders,read_themes,write_themes,write_content,read_content,write_script_tags,read_script_tags,read_checkouts,write_checkouts' % (s_url, api_key)
        
        li = link.strip("/")
       
        redirect = HttpResponseRedirect(f'{li}')
       
    return redirect
# installation process functional code end #

# redirect to app fucntional code start (while successfully installed redirect to app) #
def redirect(request):
    if request.GET.get('shop') is not None:     # check request data is not none #
        shop = request.GET.get('shop')
        redir = HttpResponseRedirect(redirect_to='https://' + shop + '/admin/apps/6developerorderapp')
    return redir
# redirect to app fucntional code end #

# Uninstall Webhook functional code start (to create webhook) #
def unistaller_second(request):
    if len(shop) != 0:              # check the length of shop #
        webrec = installer.objects.filter(shop=shop)        # filter installer data by shop#
        if webrec:
            token = webrec[0].access_token
            hmac_data = webrec[0].hmac
        else:
            HttpResponse("Invalid shop detail")

        url = "https://" + shop + "/admin/api/2020-07/webhooks.json"

        headers = {
            'X-Shopify-Access-Token': token,
            'X-Shopify-Topic': 'app/uninstalled',
            'X-Shopify-Hmac-Sha256': hmac_data,
            'X-Shopify-Shop-Domain': shop,
            'X-Shopify-API-Version': API_VERSION
        } 

        my = {
            "webhook": {
                "topic": "app/uninstalled",
                "address": 'https://raffle.pagekite.me/uninstall',  # uninstall process data send on the address #
                "format": "json"
            }
        }
    
        r = requests.post(url=url, json=my, headers=headers)
        c = json.loads(r.text)
        return HttpResponse(json.dumps(c), content_type="application/json")
# Uninstall Webhook functional code start

# app install final step functional code start (to add shop data into database) #
@xframe_options_exempt
def final(request):
    my_dict = dict()
    if request.GET.get('hmac') is not None:         # check hmac is not none #
        hmac = request.GET.get('hmac')
        global shop
        shop = request.GET.get('shop')

        if request.GET.get('code') is not None:     # check code is not none #
            code = request.GET.get('code')
            if len(code) != 0:              # check length of code #
                record = installer.objects.filter(shop=shop)    # filter installer data by shop #
                if record:
                    get_code = record[0].code
                    get_access_token = record[0].access_token
                    return redirect(request=request)
                else:
                    accesstoken = token(code=code, shop=shop)       # call token function to generate access_token #
                    rec = installer()           # call installer to add record #
                    rec.shop = shop
                    rec.code = code
                    rec.hmac = hmac
                    rec.access_token = accesstoken['access_token']
                    rec.save()      # save data in installer table #

                    tokn = accesstoken['access_token']
                    
                    a = unistaller_second(request=request)          # call 'unistaller_second' to create webhook #
                    print(a, "pragnesh")
                    return redirect(request=request)            # redirect to app #
                return redirect(request=request)
        else:
            record = installer.objects.filter(shop=shop)        # filter installer data by shop #    
            if record:
                getaccess = record[0].access_token
                getshop = record[0].shop
                global get_tkn
                get_tkn = getaccess
                return render(request, 'final.html')
            else:
                return HttpResponse("No Data Found")
    else:
        return render(request, 'login.html')
# app install final step functional code end #

# Display Product Code Start #
@xframe_options_exempt
def product(request):
    if request.method == "POST":
        pass
    else:
        url = "https://%s/admin/api/%s/products.json" % (shop, API_VERSION)

        header = {
            'X-Shopify-Access-Token': get_tkn,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }

        r = requests.get(url=url, headers=header)
        if r.status_code == 200:
            product_dict = dict()
            product_list = list()
            
            c = json.loads(r.text)
            for x in c['products']:
                product_variant_list = list()
                for variant in x['variants']:
                    sub_variant_dict = {
                        'variant_id': variant['id'],
                        'variant_title': variant['title'],
                        'variant_quantity': variant['inventory_quantity']
                    }
                    product_variant_list.append(sub_variant_dict)
                sub_product_dict = {
                    'id': x['id'],
                    'title': x['title'],
                    'variants': product_variant_list
                }
                product_list.append(sub_product_dict)
            product_dict = product_list
            from django.core.paginator import Paginator
            paginator = Paginator(product_dict, 10)   
            page = request.GET.get('page')
            posts = paginator.get_page(page)
        return render(request, 'product.html', {'product': posts})
# Display Product Code End #

# Raffle Creation Code Start #
@csrf_exempt
def raffle(request): 
    if request.method == "GET":
        productid = request.GET['product']
        variantid = request.GET['variant']
        return render(request, 'raffle.html', {'product': productid, 'variant': variantid})
    else: 
        if (request.POST['startdate'] is not None and request.POST['startdate'] != '') and (request.POST['enddate'] is not None and request.POST['enddate'] != '') and (request.POST['content'] is not None and request.POST['content'] != '') and (request.POST['get_product'] is not None and request.POST['get_product'] != '') and (request.POST['get_variant'] is not None and request.POST['get_variant'] !=''):
            check_variant_quantity = Required_api.get_variant_quantity(varid=request.POST['get_variant'], shop=shop, token=get_tkn)
            if check_variant_quantity:
                auto = ''
                from django.utils.datastructures import MultiValueDictKeyError
                try:
                    auto = request.POST['automatic']
                    if auto == "true":
                        auto = True
                except MultiValueDictKeyError:
                    auto = False

                check_installer = installer.objects.filter(shop=shop)
                if check_installer:
                    check_product_raffle = Product_Raffle.objects.filter(product_id=request.POST['get_product'], variant_id=request.POST['get_variant'])
                    if check_product_raffle:
                        return render(request, 'raffle.html', messages.success(request, "Raffle already created"))
                    else:
                        create_raffle = Raffle.objects.create(is_automatic=auto, start_date=request.POST['startdate'], end_date=request.POST['enddate'], content=request.POST['content'], installer_id_id=check_installer[0].id)
                        if create_raffle.pk:
                            create_product_raffle = Product_Raffle.objects.create(product_id=request.POST['get_product'], variant_id=request.POST['get_variant'], Raffle_id_id=create_raffle.pk)
                            if create_product_raffle.pk:
                                return render(request, 'raffle.html', messages.success(request, "Raffle Created Successfully"))
                            else:
                                return render(request, 'raffle.html', messages.success(request, "Raffle Product Relation Not Created"))
                        else:
                            return render(request, 'raffle.html', messages.success(request, "Raffle Not Created"))
                else:
                    return render(request, 'raffle.html', messages.success(request, "Shop Detail Not Found"))
            else:
                return render(request, 'raffle.html', messages.success(request, "Variant quantity out of stock"))    
        else:
            return render(request, 'raffle.html', messages.success(request, "Some Fields Are Missing"))
# Raffle Creation Code End #

# Get New Raffle Detail #
@xframe_options_exempt
def new_raffle(request):
    raffle_list = list()
    raffle_dict = dict()
    if request.method == "GET":
        check_installer = installer.objects.filter(shop=shop)
        if check_installer:
            check_raffle_data = Raffle.objects.filter(installer_id_id=check_installer[0].id, is_deleted=False, is_active=True, is_new=True)
            if check_raffle_data:
                for x in check_raffle_data:
                    sub_raffle_detail = {
                        'startdate': x.start_date,
                        'enddate': x.end_date,
                        'content': x.content,
                        'is_activate': x.is_active,
                        'raffle_id': x.id,
                    }
                    raffle_list.append(sub_raffle_detail)
                raffle_dict['raffle'] = raffle_list
                from django.core.paginator import Paginator
                paginator = Paginator(raffle_dict['raffle'], 5)   
                page = request.GET.get('page')
                posts = paginator.get_page(page)
                return render(request, 'new_raffle.html', {'data': posts})
            else:
                return render(request, 'new_raffle.html', messages.error(request, "raffle is not found"))
        else:
            return render(request, 'new_raffle.html', messages.error(request, "store data not found"))

# Get New Raffle Detail With Subscribers Basic Detail #
@xframe_options_exempt
@csrf_exempt
def get_new_raffle_detail(request):
    raffle_list = list()
    raffle_dict = dict()
    if request.method == "GET":
        if request.GET.get('raffle_id') is not None and request.GET.get('raffle_id') != '':
            check_installer = installer.objects.filter(shop=shop)
            if check_installer:
                check_raffle = Raffle.objects.filter(id=request.GET.get('raffle_id'), installer_id_id=check_installer[0].id, is_deleted=False, is_active=True, is_new=True)
                if check_raffle:
                    check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=check_raffle[0].id)
                    if check_product_raffle:
                        check_subscribers = Subscribers.objects.filter(product_raffle_id_id=check_product_raffle[0].id, is_deleted=False, is_active=True)
                        if check_subscribers:
                            for x in check_subscribers:
                                sub_subscriber_dict = {
                                    'Customer_id':x.customerid,
                                    'Created_date':x.createddate,
                                    'is_active':x.is_active,
                                    'raffle_id':request.GET.get('raffle_id'),
                                }
                                raffle_list.append(sub_subscriber_dict)
                            raffle_dict['Subscribers'] = raffle_list
                            from django.core.paginator import Paginator
                            paginator = Paginator(raffle_dict['Subscribers'], 5)   
                            page = request.GET.get('page')
                            posts = paginator.get_page(page)
                            return render(request, 'subscriber.html', {'subscriber':posts})
                        else:
                            return render(request, 'subscriber.html', messages.error(request, "Raffle Have not any customer"))
                    else:   
                        return render(request, 'subscriber.html', messages.error(request, "Product raffle detail not found"))
                else:   
                    return render(request, 'subscriber.html', messages.error(request, "Raffle detail not found"))
            else:
                return render(request, 'subscriber.html', messages.error(request, "Shop detail not found"))
        else:
            return render(request, 'subscriber.html', messages.error(request, "Please select valid raffle"))


# Get New Raffle Subscriber Full Detail #
@xframe_options_exempt
@csrf_exempt
def subscribers(request): 
    customer_detail_dict = dict()
    if request.method == "POST":
        if (request.POST['subscriber_id'] is not None and request.POST['subscriber_id']!= '' and request.POST['raffle_id'] is not None and request.POST['raffle_id'] != ''):
            check_store = installer.objects.filter(shop=shop)
            if check_store:
                # print('1')
                check_raffle = Raffle.objects.filter(id=request.POST['raffle_id'],installer_id_id=check_store[0].id, is_deleted=False, is_active=True)
                if check_raffle:
                    # print('2')
                    check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=check_raffle[0].id, is_deleted=False)
                    if check_product_raffle:
                        # print(check_product_raffle[0].id, request.POST['subscriber_id'])
                        check_customer = Subscribers.objects.filter(product_raffle_id_id=check_product_raffle[0].id, customerid=request.POST['subscriber_id'], is_deleted=False, is_active=True, is_winner=None)
                        if check_customer:
                            from .subscriber_details import get_detail
                            subscriber_detail = get_detail(Token=get_tkn, SHOP=shop, Customerid=check_customer[0].customerid)
                            if subscriber_detail != {}:
                                customer_detail_dict = subscriber_detail
                            else:
                                customer_detail_dict = ''
                        else:
                            return render(request, 'subscriber.html', messages.error(request, "Invalid Subscriber"))
                    else:
                        return render(request, 'subscriber.html', messages.error(request, "Product Raffle Detail not found"))
                else:
                    return render(request, 'subscriber.html', messages.error(request, "Invalid Raffle Detail"))
            else:
                return render(request, 'subscriber.html', messages.error(request, "Invalid Store Detail"))
        else:
            return render(request, 'subscriber.html', messages.error(request, "Invalid Subscriber Id"))
        return render(request, 'subscriber.html', {'detail':customer_detail_dict, 'shop':shop})

# Get Old Raffle Detail #
@xframe_options_exempt
@csrf_exempt
def old_raffle(request):
    raffle_list = list()
    raffle_dict = dict()
    if request.method == "GET":
        check_installer = installer.objects.filter(shop=shop)
        if check_installer:
            check_raffle_data = Raffle.objects.filter(installer_id_id=check_installer[0].id, is_deleted=False, is_active=False, is_new=False)
            if check_raffle_data:
                for x in check_raffle_data:
                    sub_raffle_detail = {
                        'startdate': x.start_date,
                        'enddate': x.end_date,
                        'content': x.content,
                        'is_activate': x.is_active,
                        'raffle_id': x.id,
                    }
                    raffle_list.append(sub_raffle_detail)
                raffle_dict['raffle'] = raffle_list
                from django.core.paginator import Paginator
                paginator = Paginator(raffle_dict['raffle'], 5)   
                page = request.GET.get('page')
                posts = paginator.get_page(page)
                return render(request, 'old_raffle.html', {'data':posts})
            else:
                return render(request, 'old_raffle.html', messages.error(request, "raffle is not found"))
        else:
            return render(request, 'old_raffle.html', messages.error(request, "store data not found"))

# Get Old Raffle Subscribers Basic Detail  #
@xframe_options_exempt
def get_old_raffle_detail(request):
    raffle_dict = dict()
    raffle_list = list()
    if request.method == "GET":
        if (request.GET.get('raffle_id') is not None and request.GET.get('raffle_id') != ''):
            check_installer = installer.objects.filter(shop=shop)
            if check_installer:
                check_raffle = Raffle.objects.filter(id=request.GET.get('raffle_id'), installer_id_id=check_installer[0].id, is_deleted=False, is_active=False, is_new=False)
                if check_raffle:
                    check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=check_raffle[0].id)
                    if check_product_raffle:
                        check_subscribers = Subscribers.objects.filter(product_raffle_id_id=check_product_raffle[0].id, is_deleted=False, is_active=True)
                        if check_subscribers:
                            for x in check_subscribers:
                                sub_subscriber_dict = {
                                    'Customer_id':x.customerid,
                                    'Created_date':x.createddate,
                                    'is_active':x.is_active,
                                    'is_winner':x.is_winner,
                                    'raffle_id':request.GET.get('raffle_id'),
                                }
                                raffle_list.append(sub_subscriber_dict)
                            raffle_dict['Subscribers'] = raffle_list
                            from django.core.paginator import Paginator
                            paginator = Paginator(raffle_dict['Subscribers'], 5)   
                            page = request.GET.get('page')
                            posts = paginator.get_page(page)
                            return render(request, 'old_subscriber.html', {'subscriber':posts})
                        else:
                            # subscriber_dict['error'] = "Raffle Have not any customer"
                            return render(request, 'old_subscriber.html', messages.error(request, "Raffle Have not any customer"))
                    else:
                        # subscriber_dict['error'] = "Product raffle detail not found"
                        return render(request, 'old_subscriber.htmll', messages.error(request, "Product raffle detail not found"))
                else:
                    # subscriber_dict['error'] = "Raffle detail not found"
                    return render(request, 'old_subscriber.html', messages.error(request, "Raffle detail not found"))
            else:
                # subscriber_dict['error'] = "Shop detail not found"
                return render(request, 'old_subscriber.html', messages.error(request, "Shop detail not found"))
        else:
            return render(request, 'old_subscriber.html', messages.error(request, "Please select valid raffle"))

# Get Subscriber Full Detail #
@xframe_options_exempt
@csrf_exempt
def old_subscribers(request):
    customer_detail_dict = dict()
    if request.method == "POST":
        if (request.POST['subscriber_id'] is not None and request.POST['subscriber_id']!= '' and request.POST['raffle_id'] is not None and request.POST['raffle_id'] != ''):
            check_store = installer.objects.filter(shop=shop)
            if check_store:
                check_raffle = Raffle.objects.filter(id=request.POST['raffle_id'],installer_id_id=check_store[0].id, is_deleted=False, is_active=False, is_new=False)
                if check_raffle:
                    check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=check_raffle[0].id, is_deleted=False)
                    if check_product_raffle:
                        check_customer = Subscribers.objects.filter(product_raffle_id_id=check_product_raffle[0].id, customerid=request.POST['subscriber_id'], is_deleted=False, is_active=True)
                        if check_customer:
                            from .subscriber_details import get_detail
                            subscriber_detail = get_detail(Token=get_tkn, SHOP=shop, Customerid=check_customer[0].customerid)
                            if subscriber_detail != {}:
                                customer_detail_dict = subscriber_detail
                            else:
                                customer_detail_dict = ''
                        else:
                            return render(request, 'old_subscriber.html', messages.error(request, "Invalid Subscriber"))
                    else:
                        return render(request, 'old_subscriber.html', messages.error(request, "Product Raffle Detail not found"))
                else:
                    return render(request, 'old_subscriber.html', messages.error(request, "Invalid Raffle Detail"))
            else:
                return render(request, 'old_subscriber.html', messages.error(request, "Invalid Store Detail"))
        else:
            return render(request, 'old_subscriber.html', messages.error(request, "Invalid Subscriber Id"))
        return render(request, 'old_subscriber.html', {'detail':customer_detail_dict, 'shop':shop})

# Dashboard #
@xframe_options_exempt
def dashboard(request):
    dashboard_dict = dict()
    dashboard_raffle_list = list()
    dashboard_winner_list = list()
    address = ''
    if request.method == "GET":
        check_store = installer.objects.filter(shop=shop)
        if check_store:
            check_raffle = Raffle.objects.filter(installer_id_id=check_store[0].id, is_active=True, is_new=True, is_deleted=False)
            if check_raffle:
                for x in check_raffle:
                    check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=x.id)
                    if check_product_raffle:
                        sub_dashboard_dict = {
                            'raffle_start':x.start_date,
                            'raffle_end':x.end_date,
                            'raffle_content':x.content,
                            'raffle_product_id':check_product_raffle[0].product_id,
                            'raffle_variant_id':check_product_raffle[0].variant_id,
                        }
                        dashboard_raffle_list.append(sub_dashboard_dict)
                    else:
                        return render(request, 'Dashboard.html', messages.error(request, 'Raffle Product not found'))
            else:
                return render(request, 'Dashboard.html', messages.error(request, 'Raffle detail not found'))
        else:
            return render(request, 'Dashboard.html', messages.error(request, 'Store detail not found'))
        
        check_subscribers = Subscribers.objects.filter(is_deleted=False, is_active=True, is_winner=True)
        if check_subscribers:
            for z in check_subscribers:
                from .subscriber_details import get_detail
                get_subscriber_detail = get_detail(APIKEY=API_KEY, APIVERSION=API_VERSION, SHAREDSECRET=SHARED_SECRET, Token=get_tkn, SHOP=shop, Customerid=z.customerid)
                if get_subscriber_detail != {}:
                    if get_subscriber_detail['customer']['default_address']['address2'] != '':
                        address = get_subscriber_detail['customer']['default_address']['address1'] + "," + get_subscriber_detail['customer']['default_address']['address2'] + "," + get_subscriber_detail['customer']['default_address']['city'] + "-" + get_subscriber_detail['customer']['default_address']['zip'] + "," + get_subscriber_detail['customer']['default_address']['province'] + "," + get_subscriber_detail['customer']['default_address']['country'] 
                    else:
                        address = get_subscriber_detail['customer']['default_address']['address1'] + "," + get_subscriber_detail['customer']['default_address']['city'] + "-" + get_subscriber_detail['customer']['default_address']['zip'] + "," + get_subscriber_detail['customer']['default_address']['province'] + "," + get_subscriber_detail['customer']['default_address']['country'] 
                    sub_subscriber_dict = {
                        'fullname':get_subscriber_detail['customer']['first_name'] + " " + get_subscriber_detail['customer']['last_name'],
                        'address':address,
                        'email':get_subscriber_detail['customer']['email'],
                        'phone':get_subscriber_detail['customer']['phone'],
                    }
                    dashboard_winner_list.append(sub_subscriber_dict)
                else:
                    sub_subscriber_dict = {

                    }
                    dashboard_winner_list.append(sub_subscriber_dict)
        else:
            sub_subscriber_dict = {
                'error': "Winners detail not found"
            }
            dashboard_winner_list.append(sub_subscriber_dict)
        
        dashboard_dict['raffle'] = dashboard_raffle_list
        dashboard_dict['winner'] = dashboard_winner_list

        from django.core.paginator import Paginator
        paginator = Paginator(dashboard_dict['raffle'], 1)   
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        paginator1 = Paginator(dashboard_dict['winner'], 1)   
        page1 = request.GET.get('page')
        posts1 = paginator1.get_page(page1)
        return render(request, 'Dashboard.html', {'raffle': posts, 'winner':posts1})


# Delete Subscriber Code #
@xframe_options_exempt
def delete_subscriber(request):
    if request.method == 'GET':
        if (request.GET.get('raffleid') is not None and request.GET.get('raffleid') != '' and request.GET.get('customerid') is not None and request.GET.get('customerid') != ''):
            # subscriber = request.GET.get('customerid')
            # raffledata = request.GET.get('raffleid')
            print(request.GET.get('customerid'), request.GET.get('raffleid'))
            check_raffle = Raffle.objects.filter(id=request.GET.get('raffleid'), is_active=True, is_new=True, is_deleted=False)
            if check_raffle:
                check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=check_raffle[0].id)
                if check_product_raffle:
                    check_subscribers = Subscribers.objects.filter(product_raffle_id_id=check_product_raffle[0].id, is_active=True, customerid=request.GET.get('customerid'), is_winner=False, is_deleted=False).update(is_deleted=True, is_active=False)
                    if check_subscribers:
                        return HttpResponse('Subscriber Deleted Successfully')
                    else:
                        return render(request, 'new_raffle.html', messages.error(request, 'subscriber not deleted'))
            else:
                return render(request, 'new_raffle.html', messages.error(request, 'raffle detail not found'))
        else:
            return render(request, 'new_raffle.html', messages.error(request, 'some fields are missing')) 

# Create Winner Email For New/Active Raffle #
@csrf_exempt
def WinnerEmailTemplate(request):
    if request.method == "GET":
        if (request.GET.get('raffle_id') is not None and request.GET.get('raffle_id') != ''):
            return render(request, 'CreateWinner.html', {'raffle_id': request.GET.get('raffle_id')})
        else:
            return render(request, 'new_raffle.html', messages.error(request, 'Raffle Detail not found'))
    else:
        if (request.POST['raffle_id'] is not None and request.POST['raffle_id'] != '' and request.POST['content'] is not None and request.POST['content'] != ''):
            check_installer = installer.objects.filter(shop=shop)
            if check_installer:
                # Ongoing Raffle #
                check_new_raffle = Raffle.objects.filter(id=request.POST['raffle_id'], installer_id_id=check_installer[0].id, is_active=True, is_deleted=False, is_new=True)
                if check_new_raffle:
                    check_winner_email = WinnderEmail.objects.filter(installer_id_id=check_installer[0].id, Raffle_id_id=check_new_raffle[0].id)
                    if check_winner_email:
                        return render(request, 'CreateWinner.html', messages.error(request, 'Winner Email Template Already Created'))
                    else:
                        create_winner_email = WinnderEmail.objects.create(winnertemplate=request.POST['content'], installer_id_id=check_installer[0].id, Raffle_id_id=check_new_raffle[0].id)
                        if create_winner_email.pk:
                            return render(request, 'CreateWinner.html', messages.success(request, 'Ongoing Winner Email Templates Created'))
                        else:
                            return render(request, 'CreateWinner.html', messages.error(request, 'Ongoing Winner Email Templates Not Created'))
                else:           
                    return render(request, 'CreateWinner.html', messages.error(request, 'Invalid Raffle Id'))
            else:
                return render(request, 'CreateWinner.html', messages.error(request, 'Invalid Store Detail'))
        else:
            return render(request, 'CreateWinner.html', messages.error(request, 'Some fields are missing'))

# Create Lost Email For New/Active Raffle #   
@csrf_exempt
def LoserEmailTemplate(request):
    if request.method == "GET":
        if (request.GET.get('raffle_id') is not None and request.GET.get('raffle_id') != ''):
            return render(request, 'CreateLoser.html', {'raffle_id': request.GET.get('raffle_id')})
        else:
            return render(request, 'new_raffle.html', messages.error(request, 'Raffle Detail not found'))
    else:
        if (request.POST['raffle_id'] is not None and request.POST['raffle_id'] != '' and request.POST['content'] is not None and request.POST['content'] != ''):
            check_installer = installer.objects.filter(shop=shop)
            if check_installer:
                # Ongoing Raffle #
                check_new_raffle = Raffle.objects.filter(id=request.POST['raffle_id'], installer_id_id=check_installer[0].id, is_active=True, is_deleted=False, is_new=True)
                if check_new_raffle:
                    check_loser_email = LoserEmail.objects.filter(installer_id_id=check_installer[0].id, Raffle_id_id=check_new_raffle[0].id)
                    if check_loser_email:
                        return render(request, 'CreateLoser.html', messages.error(request, 'Loser Email Templates Already Created'))
                    else:
                        create_Loser_email = LoserEmail.objects.create(losertemplate=request.POST['content'], installer_id_id=check_installer[0].id, Raffle_id_id=check_new_raffle[0].id)
                        if create_Loser_email.pk:
                            return render(request, 'CreateLoser.html', messages.success(request, 'Ongoing Loser Email Templates Created'))
                        else:
                            return render(request, 'CreateLoser.html', messages.error(request, 'Ongoing Loser Email Templates Not Created'))
                else:           
                    return render(request, 'CreateLoser.html', messages.error(request, 'Invalid Raffle Id'))
            else:
                return render(request, 'CreateLoser.html', messages.error(request, 'Invalid Store Detail'))
        else:
            return render(request, 'CreateLoser.html', messages.error(request, 'Some fields are missing'))

# Upcoming Raffle Detail #
@xframe_options_exempt
def upcoming_raffle(request):
    raffle_dict = dict()
    upcoming_raffle_list = list()
    ongoing_raffle_list = list()
    old_raffle_list = list()
    if request.method == "GET":
        check_installer = installer.objects.filter(shop=shop)
        if check_installer:
            check_upcoming_raffle = Raffle.objects.filter(installer_id_id=check_installer[0].id, is_deleted=False, is_active=True, is_new=None)
            if check_upcoming_raffle:
                for x in check_upcoming_raffle:
                    check_upcoming_raffle_product = Product_Raffle.objects.filter(Raffle_id_id=x.id)
                    if check_upcoming_raffle_product:
                        sub_upcoming_raffle = {
                            'raffle_start':x.start_date,
                            'raffle_end':x.end_date,
                            'raffle_content':x.content,
                            'raffle_product':check_upcoming_raffle_product[0].product_id,
                            'raffle_variant':check_upcoming_raffle_product[0].variant_id,
                            'raffle_is_new':x.is_new,
                            'raffle_id':x.id,
                        }
                        upcoming_raffle_list.append(sub_upcoming_raffle)
            else:
                sub_upcoming_raffle = {
                    'error': 'Coming soon'
                }
                upcoming_raffle_list.append(sub_upcoming_raffle)
            
            from django.core.paginator import Paginator
            paginator = Paginator(upcoming_raffle_list, 3)   
            page = request.GET.get('page')
            upcoming_posts = paginator.get_page(page)
        return render(request, 'upcoming_raffle.html', {'upcoming':upcoming_posts})

# create upcoming raffle lost email #
@csrf_exempt
def UpcomingLoserEmail(request):
    if request.method == "GET":
        if (request.GET.get('raffle_id') is not None and request.GET.get('raffle_id') != ''):
            return render(request, 'CreateUpcomingLoser.html', {'raffle_id': request.GET.get('raffle_id')})
        else:
            return render(request, 'upcoming_raffle.html', messages.error(request, 'Raffle Detail not found'))
    else:
        if (request.POST['raffle_id'] is not None and request.POST['raffle_id'] != '' and request.POST['content'] is not None and request.POST['content'] != ''):
            check_installer = installer.objects.filter(shop=shop)
            if check_installer:
                # Ongoing Raffle #
                check_new_raffle = Raffle.objects.filter(id=request.POST['raffle_id'], installer_id_id=check_installer[0].id, is_active=True, is_deleted=False, is_new=None)
                if check_new_raffle:
                    check_loser_email = LoserEmail.objects.filter(installer_id_id=check_installer[0].id, Raffle_id_id=check_new_raffle[0].id)
                    if check_loser_email:
                        return render(request, 'CreateUpcomingLoser.html', messages.error(request, 'Upcoming Loser Email Templates Already Created'))
                    else:
                        create_Loser_email = LoserEmail.objects.create(losertemplate=request.POST['content'], installer_id_id=check_installer[0].id, Raffle_id_id=check_new_raffle[0].id)
                        if create_Loser_email.pk:
                            return render(request, 'CreateUpcomingLoser.html', messages.success(request, 'Upcoming Loser Email Templates Created'))
                        else:
                            return render(request, 'CreateUpcomingLoser.html', messages.error(request, 'Upcoming Loser Email Templates Not Created'))
                else:           
                    return render(request, 'CreateUpcomingLoser.html', messages.error(request, 'Invalid Raffle Id'))
            else:
                return render(request, 'CreateUpcomingLoser.html', messages.error(request, 'Invalid Store Detail'))
        else:
            return render(request, 'CreateUpcomingLoser.html', messages.error(request, 'Some fields are missing'))

# create upcoming raffle Winner email #
@csrf_exempt
def UpcomingWinnerEmail(request):
    if request.method == "GET":
        if (request.GET.get('raffle_id') is not None and request.GET.get('raffle_id') != ''):
            return render(request, 'CreateUpcomingWinner.html', {'raffle_id': request.GET.get('raffle_id')})
        else:
            return render(request, 'upcoming_raffle.html', messages.error(request, 'Raffle Detail not found'))
    else:
        if (request.POST['raffle_id'] is not None and request.POST['raffle_id'] != '' and request.POST['content'] is not None and request.POST['content'] != ''):
            check_installer = installer.objects.filter(shop=shop)
            if check_installer:
                # Upcoming Raffle #
                check_upcoming_raffle = Raffle.objects.filter(id=request.POST['raffle_id'], installer_id_id=check_installer[0].id, is_active=True, is_deleted=False, is_new=None)
                if check_upcoming_raffle:
                    check_winner_email = WinnderEmail.objects.filter(installer_id_id=check_installer[0].id, Raffle_id_id=check_upcoming_raffle[0].id)
                    if check_winner_email:
                        return render(request, 'CreateUpcomingWinner.html', messages.error(request, 'Upcoming Winner Email Templates Already Created'))
                    else:
                        create_upcoming_winner_email = WinnderEmail.objects.create(winnertemplate=request.POST['content'], installer_id_id=check_installer[0].id, Raffle_id_id=check_upcoming_raffle[0].id)  
                        if create_upcoming_winner_email.pk:
                            return render(request, 'CreateUpcomingWinner.html', messages.success(request, 'Upcoming Winner Email Templates Created'))
                        else:
                            return render(request, 'CreateUpcomingWinner.html', messages.error(request, 'Upcoming Winner Email Templates Not Created'))
                else:
                    return render(request, 'CreateUpcomingWinner.html', messages.error(request, 'Invalid Raffle Id'))
            else:
                return render(request, 'CreateUpcomingWinner.html', messages.error(request, 'Invalid Store Detail'))
        else:
            return render(request, 'CreateUpcomingWinner.html', messages.error(request, 'Some fields are missing'))

# Front-End for subscribe user to raffle/ Create subscriber #
def create_customer(request):
    if request.method == "GET":
        if (request.GET.get('raffle') is not None and request.GET.get('raffle') != '' and request.GET.get('customer') is not None and request.GET.get('customer') != '' and request.GET.get('shopdata') is not None and request.GET.get('shopdata') != ''):
            check_installer = installer.objects.filter(shop=request.GET.get('shopdata'))
            if check_installer:
                check_raffle = Raffle.objects.filter(id=request.GET.get('raffle'), is_active=True, is_deleted=False, is_new=True, installer_id_id=check_installer[0].id)
                if check_raffle:
                    from .models import Subscribers, Product_Raffle
                    check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=check_raffle[0].id)
                    if check_product_raffle:
                        check_customer = Subscribers.objects.filter(customerid=request.GET.get('customer'), product_raffle_id_id=check_product_raffle[0].id)
                        if check_customer:
                            return HttpResponse('User already subscribed this raffle')
                        else:
                            create_customer = Subscribers.objects.create(customerid=request.GET.get('customer'), product_raffle_id_id=check_product_raffle[0].id)
                            if create_customer.pk:
                                return HttpResponse('user created successfully')
                            else:
                                return HttpResponse('user not created successfully')
                    else:
                        return HttpResponse('Raffle product not found')
                else:
                    return HttpResponse('Invalid raffle id')
            else:
                return HttpResponse('Invalid shop detail')
        else:
            return HttpResponse('Some fields are missing')

# Front-End check Raffle #
def check_raffle_activation(request):
    if request.method == "GET":
        # sub_dict = dict()
        if (request.GET.get('shop') is not None and request.GET.get('shop') != '' and request.GET.get('variant') is not None and request.GET.get('variant') != ''):
            product_id = ''
            shop_id = ''

            shop = request.GET.get('shop')

            token = ''
            check_installer = installer.objects.filter(shop=shop)
            if check_installer:
                shop_id = check_installer[0].id
                token = check_installer[0].access_token
            else:
                return HttpResponse('Invalid Store Detail')

            url = "https://%s/admin/api/%s/graphql.json" % (shop, API_VERSION)

            headers = {
                "X-Shopify-Access-Token": token
            }

            query = '''
            {
            productVariants(first:1,query:"id:%s")
            {
                edges
                {
                node
                {
                    product
                    {
                    id
                    }
                }
                }
            }
            }
            ''' % request.GET.get('variant')

            r = requests.post(url, json={'query':query}, headers=headers)
            if r.status_code == 200:
                c = json.loads(r.text)
                product_id = c['data']['productVariants']['edges'][0]['node']['product']['id']
                product_id = product_id.strip('gid://shopify/Product/')
            else:
                product_id = ''

            check_raffle_product = Product_Raffle.objects.filter(product_id=product_id, variant_id=request.GET.get('variant')) 
            if check_raffle_product:
                print(shop_id)
                check_raffle = Raffle.objects.filter(id=check_raffle_product[0].Raffle_id_id, installer_id_id=shop_id, is_active=True, is_deleted=False, is_new=True)
                print(check_raffle)
                if check_raffle:
                    sub_dict = {
                        'data': {
                            'raffle_id':check_raffle[0].id,
                            'raffle_start_date': check_raffle[0].start_date,
                            'raffle_end_date': check_raffle[0].end_date,
                            'raffle_content': check_raffle[0].content,
                            'raffle_is_active': check_raffle[0].is_active,
                            'raffle_is_deleted': check_raffle[0].is_deleted,
                            'raffle_is_new': check_raffle[0].is_new,
                            'raffle_is_automatic': check_raffle[0].is_automatic,
                        }
                    } 
                    print(sub_dict)
                    return JsonResponse(sub_dict) # Done
                else:
                    sub_dict = {
                        'error': "Raffle detail not found"
                    }
                    return HttpResponse(json.dumps(sub_dict), content_type="application/json")
            else:
                sub_dict = {
                    'error': "Invalid product detail"
                }
                return HttpResponse(json.dumps(sub_dict), content_type="application/json")
        else:
            sub_dict = {
                'error': "Some fields are missing"
            }
            return HttpResponse(json.dumps(sub_dict), content_type="application/json")

@csrf_exempt
def SelectWinnerManually(request):
    if request.method == "GET":
        subscribers_list = list()
        subscribers_dict = dict()
        get_shop = ''
        get_token = ''
        qun = ''
        if (request.GET.get('raffle_id') is not None and request.GET.get('raffle_id') != '' and request.GET.get('quntity') is not None and request.GET.get('quntity') != ''):
            check_raffle = Raffle.objects.filter(id=request.GET.get('raffle_id'), is_active=False, is_deleted=False, is_new=False, is_automatic=False)
            if check_raffle:
                check_installer = installer.objects.filter(id=check_raffle[0].installer_id_id)
                if check_installer:
                    get_shop = check_installer[0].shop
                    get_token = check_installer[0].access_token
                else:
                    return render(request, 'ManualSelectWinner.html', messages.error(request, 'Invalid Shop Detail'))

                check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=check_raffle[0].id, is_deleted=False)
                if check_product_raffle:
                    check_subscribers = Subscribers.objects.filter(product_raffle_id_id=check_product_raffle[0].id, is_deleted=False, is_active=True, is_winner=None)
                    if check_subscribers:
                        for x in check_subscribers:
                            get_detail = Required_api.get_subscriber(subscriber_id=x.customerid, shop=get_shop, token=get_token)
                            if get_detail:
                                fullname = get_detail['customer']['first_name'] + " " + get_detail['customer']['last_name']
                                email = get_detail['customer']['email']
                                phone = get_detail['customer']['phone']
                                id = get_detail['customer']['id']
                                sub_dict = {
                                    'id': id,
                                    'fullname': fullname,
                                    'email':email,
                                    'phone':phone 
                                }
                                subscribers_list.append(sub_dict)
                        subscribers_dict['subscribers'] = subscribers_list
                        
                    else:
                        return render(request, 'ManualSelectWinner.html', messages.error(request, 'No subscriber found'))
                else:
                    return render(request, 'ManualSelectWinner.html', messages.error(request, 'No product detail on raffle'))
            else:
                return render(request, 'ManualSelectWinner.html', messages.error(request, 'Invalid raffle detail'))
        else:
            return render(request, 'ManualSelectWinner.html', messages.error(request, 'Some fields are missing'))
        print(request.GET.get('raffle_id'), request.GET.get('quntity'), subscribers_dict)
        qun = 2
        print(subscribers_dict)
        return render(request, 'ManualSelectWinner.html', {'raffle_id':request.GET.get('raffle_id'), 'quantity':qun, 'subscribers':subscribers_dict})
    else:
        WinnerList = request.POST.getlist('winnerList[]')
        LoserList = request.POST.getlist('loserList[]')
        product_id = ''
        variant_id = ''
        product_raffle_id = ''
        get_shop = ''
        get_token = ''
        store_id = ''
        print(WinnerList, LoserList, "pragnesh")

        check_raffle = Raffle.objects.filter(id=request.POST['raffle'], is_active=False, is_deleted=False, is_new=False, is_automatic=False)
        if check_raffle:
            check_installer = installer.objects.filter(id=check_raffle[0].installer_id_id)
            if check_installer:
                get_shop = check_installer[0].shop
                get_token = check_installer[0].access_token
            else:
                return render(request, 'ManualSelectWinner.html', messages.error(request, 'Invalid Shop Detail'))
            
            check_product_raffle = Product_Raffle.objects.filter(Raffle_id_id=check_raffle[0].id)
            if check_product_raffle:
                product_raffle_id = check_product_raffle[0].id
                product_id = check_product_raffle[0].product_id
                variant_id = check_product_raffle[0].variant_id
            else:
                return render(request, 'ManualSelectWinner.html', messages.error(request, 'Invalid Product Detail'))

            vendor_email, store_id = Required_api.get_vendor_email(shop=get_shop, token=get_token)

            for x in WinnerList:
                Subscribers.objects.filter(customerid=x, product_raffle_id_id=product_raffle_id, is_active=True, is_deleted=False, is_winner=None).update(is_winner=True)
                subscriber_data = Required_api.get_subscriber(subscriber_id=x, shop=get_shop, token=get_token)
                address = subscriber_data['customer']['default_address']
                email = subscriber_data['customer']['email']
                phone = subscriber_data['customer']['phone']
                create_order = Required_api.create_pending_order(shop=get_shop, token=get_token, address=address, variant=variant_id, email=email, phone=phone, subscriber=x)
                order_id = create_order['order']['id']
                user_email = create_order['order']['email']
                order_status_url = create_order['order']['order_status_url']
                key = order_status_url.split('?key=')[1] 
                payment_url = "https://%s/%s/order_payment/%s?secret=%s" % (get_shop, store_id, order_id, key)
                SendWinnerEmail(subscriber_email=user_email, product_id=product_id, variant_id=variant_id, raffle_id=check_raffle[0].id, shop=get_shop, token=get_token, url=payment_url)

            for y in LoserList:
                Subscribers.objects.filter(customerid=y, product_raffle_id_id=product_raffle_id, is_active=True, is_deleted=False, is_winner=None).update(is_winner=False)
                subscriber_data = Required_api.get_subscriber(subscriber_id=y, shop=get_shop, token=get_token)
                SendLoserEmail(subscriber_email=subscriber_data['customer']['email'], product_id=product_id, variant_id=variant_id, raffle_id=check_raffle[0].id, shop=get_shop, token=get_token)
            return HttpResponse('Successfully Selected Winner and Loser')
        else:
            return render(request, 'ManualSelectWinner.html', messages.error(request, 'Invalid Raffle Detail'))