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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.towerhealthurgentcare.org"
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    r = session.get(base_url+"/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=92aa77e208&layout=0").json()
    for loc in r:
        city=loc['city']
        lat=loc['lat']
        lng=loc['lng']
        hour=loc['open_hours'].replace('{','').replace('}','').replace('[','').replace(']','').replace('\"','').replace('":"',':').replace('","',',')

        phone=loc['phone']
        zip=loc['postal_code']
        state=loc['state']
        address=loc['street']
        name=loc['title']
        country="US"
        storeno=loc['id']
        page_url = 'https://www.towerhealthurgentcare.org/locations/'
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
        store.append("<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
