import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    addressess = []
    payload = "action=get_all_stores&lat=&lng="
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }
    base_url = 'http://vercenterprises.com/'
    for i in range(0,34):
        jd = session.post("https://vercenterprises.com/wp-admin/admin-ajax.php",headers=headers,data=payload).json()[str(i)]
        location_name = jd['na']
        street_address = jd['st']
        city = jd['ct']
        state = jd['rg']
        zipp = jd['zp']
        country_code = jd['co']
        store_number = jd['ID']
        phone = jd['te']
        location_type = "<MISSING>"
        latitude = jd['lat']
        longitude = jd['lng']
        if jd['op']['0']=="24 Hours":
            hours_of_operation = "Monday: 24 Hours, Tuesday: 24 Hours, Wednesday: 24 Hours, Thursday: 24 Hours, Friday: 24 Hours, Saturday: 24 Hours, Sunday: 24 Hours"
        else:
            hours_of_operation = "Monday: "+jd['op']['0']+"-"+jd['op']['1']+", "+"Tuesday: "+jd['op']['2']+"-"+jd['op']['3']+", "+"Wednesday: "+jd['op']['4']+"-"+jd['op']['5']+", "+"Thursday: "+jd['op']['6']+"-"+jd['op']['7']+", "+"Friday: "+jd['op']['8']+"-"+jd['op']['9']+", "+"Saturday: "+jd['op']['10']+"-"+jd['op']['11']+", "+"Sunday: "+jd['op']['12']+"-"+jd['op']['13']
        page_url = jd['gu']
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code)
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
