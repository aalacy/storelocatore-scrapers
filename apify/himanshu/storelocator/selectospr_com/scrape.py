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
    base_url = "http://selectospr.com"
    r = session.get(base_url+"/main/wp-admin/admin-ajax.php?action=store_search&lat=18.46633&lng=-66.10572&max_results=5000000&search_radius=10&autoload=1").json()
    return_main_object = []
    for loc in r:
        name=loc['store'].strip()
        city=loc['city'].strip()
        state=loc['state'].strip()
        address=loc['address'].strip()
        if loc['address2']:
            address+=" "+loc['address2']
        zip=loc['zip'].strip()
        phone=loc['phone'].strip()
        country="US"
        hour=loc['hours']
        cleanr = re.compile('<.*?>')
        hour = re.sub(cleanr, '', hour)
        hour = re.sub(r'\s+', ' ', hour)
        lat=loc['lat'].strip()
        lng=loc['lng'].strip()
        storeno=loc['id']
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("mymotomart")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
