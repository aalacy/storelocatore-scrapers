import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('waxingthecity_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
   

 
    payload = {}
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    }

    r = session.get("https://www.waxingthecity.com/wp-content/uploads/locations.json",headers=headers).json()
    
    for q in r:
        lat = q['latitude']
        log = q['longitude']
        address1=''
        address1 = q['content']['address2']
        if address1:
            address1=address1
        address = q['content']['address']+ ' '+address1
        city = q['content']['city']
        state = q['content']['state_abbr']
        zipp = q['content']['zip']
        phone = q['content']['phone']
        page_url= q['content']['url']
        name= q['content']['title']
        hours =''
        for h in q['content']['hours']:
            open1 = datetime.strptime(h['openTime'],'%H%M').strftime("%I:%M %p")
            close =datetime.strptime(h['closeTime'],'%H%M').strftime("%I:%M %p")
            hours =hours+' '+ h['dayOfWeek'] + ' '+ open1 + ' - '+close
        store = []
        store.append("https://www.waxingthecity.com/")
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(log)
        store.append(hours)
        store.append(page_url)
        # logger.info(store)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
   

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
