import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import  pprint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('beefobradys_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.beefobradys.com"
    # conn = http.client.HTTPSConnection("guess.radius8.com")
    headers = {
        'authorization': "R8-Gateway App=shoplocal, key=guess, Type=SameOrigin",
        'cache-control': "no-cache"
    }
    addresses = []
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}
    
    k = session.get("https://locationstogo.com/beefs/pinsNearestBeefs.ashx?lat1=27.971&lon1=-82.49&range=500000000&fullbar=%25&partyroom=%25&catering=%25&breakfast=%25&onlineordering=%25", headers=header).json()
    for val in k:
        # logger.info(val['address'])
        locator_domain = base_url
        location_name =  val['title']
        street_address = val['address']
        city = val['city']
        state =  val['state']
        zip1 =  val['zip']
        country_code = 'US'
        store_number = val['storeID']
        phone = val['phone']
        if 'phone' in val:
            phone = val['phone']
        location_type = ''
        latitude = val['lat']
        longitude = val['lng']
        hours_of_operation = "<MISSING>"
        if street_address in addresses:
            continue
        addresses.append(street_address)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip1 if zip1 else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append("https://locationstogo.com/beefs/?_ga=2.240830785.370589044.1569420346-1665388586.1569248213")
        # if store[3] in addresses:
        #     continue
        # addresses.append(store[3])
        logger.info("data = " + str(store))
        logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store
        
       
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
