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
    base_url = "https://www.texaco.com"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',"Content-Type": "application/json; charset=utf-8"}
    return_main_object=[]
    r = session.get('https://www.texaco.com/api/app/techron2go/ws_getChevronTexacoNearMe_r2.aspx?callback=jQuery22306785250418595727_1564653077932&lat=37.7799273&lng=-121.97801529999998&oLat=37.7799273&oLng=-121.97801529999998&brand=ChevronTexaco&radius=35&_=1564653077933',headers=headers)
    lt=json.loads(r.text.split('jQuery22306785250418595727_1564653077932(')[1].split('})')[0]+'}')
    for loc in lt['stations']:
        name=loc['name']
        address=loc['address']
        city=loc['city']
        lat=loc['lat']
        lng=loc['lng']
        storeno=loc['id']
        phone=loc['phone']
        state=loc['state']
        zip=loc['zip']
        country="US"
        hour=''
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
        store.append("texaco")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
