
import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import requests

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
    base_url = "http://www.ntw.com"
    location_url = "http://www.carrolltire.com/bundles/sitejs?v=VOEFyQyAgPlUhblWeRxldYTL6TiQqgSqZV3oXYluW3U1"
    r = requests.get(location_url, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    p = (soup.text.split("(n){var i")[1].split(",r=function()")[0].replace("=",""))
    k = (p.replace('{','{"').replace(':','":').replace(',',',"').replace('},"{','},{').replace('," ','","').replace('.,"','.","').replace('Suite 100",','a":"b",').replace('Parkway a":"b",','Parkway", "a":"b",').replace('Suite A','a":"b')).replace('Suite 2','a":"b').replace(r"\t","").replace('"Unit B"','"Unit B":"C"').replace('Suite 600','a":"b').replace('Suite B','a":"b').replace('Unit A','a":"b').replace('Ct a":"b",','Ct", "a":"b",')
    h = json.loads(k)
    for value in h:
        street_address = value['branch_addr']
        city = value['branch_name']
        zipp  = value['branch_zip']
        phone = value['branch_phone']
        latitude = value['branch_lat']
        longitude = value['branch_lng']
        state = value['branch_state'] 
        store_number = value['branch_num']
        location_name = str(city)+","+str(state)+"("+str(store_number)+")"
        locator_domain = base_url
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append('<MISSING>' )
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
