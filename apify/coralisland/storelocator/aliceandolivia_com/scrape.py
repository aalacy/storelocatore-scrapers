import csv
import re
import pdb
from lxml import etree
import json
import usaddress
from sgrequests import SgRequests

base_url = 'https://www.aliceandolivia.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    page_url = 'https://www.aliceandolivia.com/store-locator.html'
    session = SgRequests() 
    headers = {
        "authority": "www.aliceandolivia.com",
        "path": "/on/demandware.store/Sites-aando-Site/default/Stores-FindStores?showMap=false&radius=300&postalCode=94107&radius=10000%20miles",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "referer": "https://www.aliceandolivia.com/stores/?horizontalView=true&isForm=true",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "scheme": "https"
    }
    stores = session.get('https://www.aliceandolivia.com/on/demandware.store/Sites-aando-Site/default/Stores-FindStores?showMap=false&radius=300&postalCode=94107&radius=10000%20miles', headers = headers).json()['stores']
    for store in stores:
        country = store['countryCode']
        if country.lower() not in ['us', 'ca']:
            continue
        name = store['name']
        street = store['address1']
        city = store['city']
        state = store['stateCode']
        zipcode = store['postalCode']
        latitude = store['latitude']
        longitude = store['longitude']
        phone = store['phone']
        hours = store['storeHours']
        store_number = store['ID']
        page_url = '<MISSING>'
        location_type = '<MISSING>'
        yield [base_url, page_url, name, street, city, state, zipcode, country, store_number, phone, location_type, latitude, longitude, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
