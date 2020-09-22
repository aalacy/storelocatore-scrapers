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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "zip"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_store(data, country):
    state=data['state']
    city=data['city']
    link=data['path']
    r1 = session.get(link)
    soup = BeautifulSoup(r1.text,"lxml")
    mainadd = json.loads(soup.find('script',{"type":"application/ld+json"}).text)
    store = []
    store.append("https://www.wyndhamhotels.com/dolce")
    store.append(mainadd['name'])
    store.append(mainadd['address']['streetAddress'])
    store.append(city)
    store.append(state)
    store.append(country)
    store.append("<MISSING>")
    try:
        store.append(mainadd['telephone'])
    except:
        store.append("<MISSING>")
    store.append("wyndhamhotels")
    try:
        store.append(mainadd['geo']['latitude'])
        store.append(mainadd['geo']['longitude'])
    except:
        store.append("<MISSING>")
        store.append("<MISSING>")
    store.append("<MISSING>")
    if(country=='US'):
        store.append(mainadd['address']['postalCode'].split(' - ')[0].strip().replace(" ","").replace(" ",""))
    else:
         store.append(mainadd['address']['postalCode'].strip().replace(" ",""))
    return store

def fetch_data():
    base_url = "https://www.wyndhamhotels.com/bin/propertypages.json?locale=en-us&brandId=DX"
    r = session.get(base_url).json()['subcategory']
    return_main_object = []
    for i in range(len(r)):
        country=r[i]['name']
        if country=="United States":
            country="US"
        if country=="Canada":
            country="CA"
        if "subcategory" in r[i]:
            for val in r[i]['subcategory']:
                for data in val['properties']:
                    store = parse_store(data, country)
                    return_main_object.append(store)
        else:
            for data in r[i]['properties']:
                store = parse_store(data, country)
                return_main_object.append(store)

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
