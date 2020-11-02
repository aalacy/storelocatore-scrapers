import csv
from bs4 import BeautifulSoup as bs
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('keyfood_com__foodemporium')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.keyfood.com/"

    addresses = []
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}

    for i in range(0,2):

        url = "https://keyfoodstores.keyfood.com/store/keyFood/en/store-locator?q=85029&page="+str(i)+"&radius=500000"

        response = session.get(url).json()
        for q in response['data']:
            street_address = ''
            line1 = q['line1']
            street_address = line1
            if q['line2']:
                street_address =street_address + ' '+q['line2']
            dictlist=[]
            for key, value in q['openings'].items():
                temp = " ".join([key,value])
                dictlist.append(temp)
            hours_of_operation = " ".join(dictlist)
            

            store = []
            store.append("https://www.keyfood.com/")
            store.append(q['displayName'] if q['displayName'] else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(q['town'] if q['town'] else '<MISSING>')
            store.append(q['state'] if q['state'] else '<MISSING>')
            store.append(q['postalCode'] if q['postalCode'] else '<MISSING>')
            store.append("US")
            store.append( '<MISSING>')
            store.append(q['phone'] if q['phone'] else '<MISSING>')
            store.append(q['displayName'])
            store.append(q['latitude'] if q['latitude'] else '<MISSING>')
            store.append(q['longitude'] if q['longitude'] else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append("https://www.keyfood.com/store"+q['url'] if q['url']  else '<MISSING>')
            # logger.info("===", str(store))
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield  store

   
    

   


def scrape():
    data = fetch_data()
    write_output(data)

scrape()    
