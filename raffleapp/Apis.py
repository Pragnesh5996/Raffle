from os import stat
import requests
import json
from decouple import config


API_KEY = config('API_KEY')
SHARED_SECRET = config('SHARED_SECRET')
API_VERSION = config('API_VERSION')

class Required_api:
    @staticmethod
    def get_variant_quantity(varid, shop, token):
        url = "https://%s/admin/api/%s/variants/%s.json" % (shop, API_VERSION, varid)
    
        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }

        r = requests.get(url=url, headers=header)
        if r.status_code == 200:
            c = json.loads(r.text)
            c = c['variant']['inventory_quantity']
            print(c)
            return c
        else:
            c = ''
            return c
    
    @staticmethod
    def get_product_title(product_id, shop, token):
        product_title = ''

        url = "https://%s//admin/api/%s/products/%s.json" % (shop, API_VERSION, product_id)

        headers = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }

        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            c = json.loads(r.text)
            product_title = c['product']['title']
        else:
            product_title = ''
        return product_title

    @staticmethod
    def get_variant_title(variant_id, shop, token):
        variant_title = ''

        url = "https://%s/admin/api/%s/graphql.json" % (shop, API_VERSION)

        headers = {
            "X-Shopify-Access-Token": token
        }

        query = '''
        {
        productVariants(first:1, query:"id:%s")
            {
            edges
            {
            node
            {
                title
            }
            }
        }
        }
        ''' % variant_id

        r = requests.post(url, json={'query':query}, headers=headers)
        if r.status_code == 200:
            c = json.loads(r.text)
            variant_title = c['data']['productVariants']['edges'][0]['node']['title']
        else:
            variant_title = ''
        return variant_title

    @staticmethod
    def get_subscriber(subscriber_id, shop, token):
        c = ''
        url = "https://%s/admin/api/%s/customers/%s.json" % (shop, API_VERSION, subscriber_id)

        header = {
            'X-Shopify-Access-Token': token,
            'Content-Type': 'application/json',
            'client_id': API_KEY,
            'client_secret': SHARED_SECRET
        }
        
        r = requests.get(url=url, headers=header)
        if r.status_code == 200:
            c = json.loads(r.text)
        else:
            c = ''
        return c
    
    @staticmethod
    def get_vendor_email(shop, token):
        vendor_email = ''
        vendor_id = ''
        url = "https://%s/admin/api/%s/graphql.json" % (shop, API_VERSION)

        headers = {
            "X-Shopify-Access-Token": token
        }

        query = '''
        {
            shop 
            {
                id
                name
                contactEmail
                domains
                {
                    host
                }
            }
        }
        '''

        r = requests.post(url, json={'query':query}, headers=headers)
        if r.status_code == 200:
            c = json.loads(r.text)
            shop_domain = c['data']['shop']['domains'][0]['host']
            if shop == shop_domain:
                vendor_email = c['data']['shop']['contactEmail']
                vendor_id = str(c['data']['shop']['id']).strip('gid://shopify/Shop/')
            else:
                vendor_email = ''
                vendor_id = ''

        return vendor_email, vendor_id

    @staticmethod
    def create_pending_order(shop, token, address, variant, email, phone, subscriber):
        url = "https://%s/admin/api/%s/orders.json" % (shop, API_VERSION)

        headers = {
            'X-Shopify-Access-Token': token
        }

        my = {
            "order":
            {
                "line_items":
                [{
                    "variant_id":variant,
                    "quantity":1
                }],
                "customer":{
                    "id":subscriber
                },
                "financial_status":"pending",
                "inventory_behaviour":"decrement_obeying_policy",
                "send_receipt":"true",
                "send_fulfillment_receipt":"true",
                "billing_address": address,
                "email":email,
                "phone":phone,
                "shipping_address":address,
                "fulfillment_status":"fulfilled"
            }
        }

        r = requests.post(url=url, headers=headers, json=my)
        if r.status_code == 201:
            c = json.loads(r.text)
        else: 
            c = ''
        return c