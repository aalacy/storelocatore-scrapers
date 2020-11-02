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
    base_url = "https://www.superthrifty.com"
    return_main_object=[]
    r = session.get(base_url+"/wp-admin/admin-ajax.php?action=store_search&lat=56.130366&lng=-106.34677099999999&max_results=25&search_radius=2000&autoload=1").json()
    for loc in r:
        if loc['url']:
            r1=session.get(base_url+loc['url'])
            soup=BeautifulSoup(r1.text,'lxml')
            zp=list(soup.find('h3',text=re.compile("Address")).parent.stripped_strings)
            zip=zp[-1].strip()
        else:
            zip=loc['zip'].strip()
        name=loc['store'].replace('&#8217;','\'').strip()
        address=loc['address'].strip()
        city=loc['city'].strip()
        state=loc['state'].strip()
        country=loc['country'].strip()
        if country=="Canada":
            country="CA"
        phone=loc['phone'].strip()
        lat=loc['lat'].strip()
        lng=loc['lng'].strip()
        cleanr = re.compile('<.*?>')
        hour=re.sub(cleanr, ' ',loc['hours']).strip()
        storeno=loc['id'].strip()
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
        store.append("superthrifty")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
