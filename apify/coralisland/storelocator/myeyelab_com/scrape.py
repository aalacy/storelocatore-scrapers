import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.myeyelab.com/'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

def get_value(item):
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.myeyelab.com/wp-admin/admin-ajax.php"
    headers={
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': '__zlcmid=u3iVHQUo3gQSjf; PHPSESSID=e2595350be5ebf75a31fbe178c8e065f; gclid=undefined',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }
    form_data = {
        "action": "somel_geo_store_list",
        "nonce": "69b8a277b1"
    }
    request = requests.post(url, headers=headers, data=form_data)    
    store_list = json.loads(request.text.replace('\\"', '')[2:])['data']['stores']
    for store in store_list:
        output = []
        hours = etree.HTML(store['sl_hours']).xpath('.//text()')
        output.append(base_url)
        output.append(get_value(store['sl_web_name']))
        output.append(get_value(store['sl_address']))
        output.append(get_value(store['sl_city']))
        output.append(get_value(store['sl_state']))
        output.append(get_value(store['sl_zip']))
        output.append(get_value(store['sl_country']))
        output.append(get_value(store['sl_id']))
        output.append(get_value(store['sl_phone']))
        output.append("My Eyelab - The Optical Retail Industry")
        output.append(get_value(store['sl_latitude']))
        output.append(get_value(store['sl_longitude']))
        output.append(get_value(hours))
        output_list.append(output)
    return output_list
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
