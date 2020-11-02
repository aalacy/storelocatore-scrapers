
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tirecenters_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addressess = []

    headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }
    base_url = "http://www.tirecenters.com/"
    location_url = "http://www.tirecenters.com/m/locations_lsh.cfc?method=getstoamount&myregion=all&returnformat=JSON"
    r = session.get(location_url, headers=headers).json()
    for i in range(0,50):
        city = (r[i][0])
        url = "http://www.tirecenters.com/m/locations_lsh.cfc?method=getlocs&mystate="+str(city)+"&myregion=all&returnformat=JSON"
        # logger.info(url)
        r1 = session.get(url, headers=headers).json()
        for value in r1:
            street_address = value['addr1']
            phone = value['phone']
            city = value['city']
            zipp  = value['zip']
            state = value['state'] 
            store_number = value['storenum']
            locator_domain = base_url
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append('<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append("US")
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append('<MISSING>')
            store.append('<MISSING>')
            store.append('<MISSING>')
            store.append('<MISSING>' )
            store.append("http://www.tirecenters.com/m/locations.html")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
