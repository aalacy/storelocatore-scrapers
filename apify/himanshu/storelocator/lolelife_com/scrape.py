import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.lolelife.com"
    r = requests.get(base_url+"/pages/storelocator")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    output=[]
    main=soup.find('div',{"class":'filter_locator'}).find_all('a')
    for atag in main:
        r1 = requests.get(base_url+"/apps/proxy/getStores?country="+atag['href'].split('/')[-1].strip().upper()).json()
        for location in r1:
            store=[]
            hour=re.sub(r'"+', '',location['weekday'].replace('[','').replace(']',''))
            store.append(base_url)
            store.append(location['title'].strip())
            store.append(location['address'].strip())
            store.append(location['city'].strip())
            if location['state']:
                store.append(location['state'].strip())
            else:
                store.append("<MISSING>")
            if location['postalcode']:
                store.append(location['postalcode'].strip())
            else:
                store.append("<MISSING>")
            if location['country']:
                store.append(location['country'].strip())
            else:
                store.append("<MISSING>")
            if location['store_id']:
                store.append(location['store_id'])
            else:
                store.append("<MISSING>")
            if location['phone']:
                store.append(location['phone'])
            else:
                store.append("<MISSING>")
            store.append("lolelife")
            if location['latitude']:
                store.append(location['latitude'])
            else:
                store.append("<MISSING>")
            if location['longitude']:
                store.append(location['longitude'])
            else:
                store.append("<MISSING>")
            if hour:
                store.append(hour)
            else:
                store.append("<MISSING>")
            if location['postalcode'] not in output:
                output.append(location['postalcode'])
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
