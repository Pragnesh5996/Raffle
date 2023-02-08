import requests
import json
from decouple import config

API_KEY = config('API_KEY')
SHARED_SECRET = config('SHARED_SECRET')
API_VERSION = config('API_VERSION')

def get_detail(SHOP, Customerid, Token):
    data_dict = dict()
    url = "https://%s/admin/api/%s/customers/%s.json" % (SHOP, API_VERSION, Customerid)

    header = {
        'X-Shopify-Access-Token': Token,
        'Content-Type': 'application/json',
        'client_id': API_KEY,
        'client_secret': SHARED_SECRET
    }
    
    r = requests.get(url=url, headers=header)
    if r.status_code == 200:
        c = json.loads(r.text)
        # print(c)
    else:
        c = json.loads(data_dict)
    return c

