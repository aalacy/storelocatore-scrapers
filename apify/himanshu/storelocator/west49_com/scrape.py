import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://west49.com"
    r = session.get(base_url+"/apps/api/v1/stores").json()
    return_main_object = []
    output=[]
    for loc in r['stores']:
        store=[]
        hour=''
        country=loc['address']['country']
        if loc['address']['country_code']:
            country=loc['address']['country_code']
        else:
            if country=="Canada":
                country="CA"
        for hr in loc['open_hours']:
            hour+=hr['day']+":"+hr['open_time']+"-"+hr['close_time']
        address=loc['address']['line1']
        state="<MISSING>"
        if loc['address']['state_code']:
            state=loc['address']['state_code'].strip()
        if loc['address']['line2']:
            address+=" "+loc['address']['line2']
        store.append(base_url)
        store.append(loc['address']['name'].strip())
        store.append(address.strip())
        store.append(loc['address']['city'].strip())
        store.append(state)
        store.append(loc['address']['zip'].strip())
        store.append(country.strip())
        store.append(loc['store_code'])
        if loc['phone']:
            store.append(loc['phone'])
        else:
            store.append("<MISSING>")
        store.append("west49")
        store.append(loc['address']['latitude'])
        store.append(loc['address']['longitude'])
        if hour.strip():
            store.append(hour.strip())
        else:
            store.append("<MISSING>")
        if loc['address']['zip'].strip() not in output:
            output.append(loc['address']['zip'].strip())
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
