import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.comerica.com"
    r = requests.get("https://locations.comerica.com/")
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    main=soup.find_all('script')
    for script in main:
        if re.search("var results" ,script.text):
            loc=json.loads(script.text.split('var results = ')[1].split(';')[0])
            for val in loc:
                store = []
                store.append(base_url)
                store.append('Comerica Bank ATM')
                store.append(val['location']['street']+' '+val['location']['additional'].strip())
                store.append(val['location']['city'])
                store.append(val['location']['province'])
                if val['location']['postal_code'] != None:
                    store.append(val['location']['postal_code'])
                else:
                    store.append("<MISSING>")
                store.append(val['location']['country'])
                store.append(val['location']['id'])
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(val['location']['lat'])
                store.append(val['location']['lng'])
                store.append("<MISSING>")
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
