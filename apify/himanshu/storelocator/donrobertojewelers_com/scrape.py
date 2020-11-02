import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('donrobertojewelers_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
   
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Cookie': '__cfduid=d450f638196ab6296cfedf1f3dffbcfa01600410288; PHPSESSID=d8oqtho1momkdok4dcb476ohb3; form_key=E6ZlB7clijDj4STK'
        }
    base_url = "https://www.donrobertojewelers.com"
    locations_url = "https://donrobertojewelers.com/storelocator"
    r = session.get(locations_url,headers=headers)
    soup = BeautifulSoup(r.text,'lxml')
    # logger.info(s)
    jd = str(soup).split('"locationItems": ')[1].split('                }')[0]
    json_data = json.loads(jd)

    for value in json_data:
        location_name = value['title']
        street_address = value['street']
        city = value['city']
        state = value['region']
        zipp = value['zip']
        country_code = value['country_id']
        store_number = value['store_location_number']
        phone = value['phone'].strip()
        location_type = '<MISSING>'
        latitude = value['latitude']
        longitude = value['longitude']
        hours_of_operation = '<MISSING>'
        page_url = '<MISSING>'

        store = []
        store.append("https://www.donrobertojewelers.com")
        store.append(location_name if location_name else "<MISSING>" )
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")   
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else"<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else"<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>" )  
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
