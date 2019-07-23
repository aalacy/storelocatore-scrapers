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
    base_url = "https://www.liquordepot.ca"
    r = requests.get(base_url+"/Our-Stores")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('script')
    for script in main:
        if "var storeList" in script.text:
            print(len(json.loads(script.text.split('var storeList =')[1].split('//]]>')[0],strict=False)))
            for data in json.loads(script.text.split('var storeList =')[1].split('//]]>')[0],strict=False):
                store=[]
                store.append(base_url)
                store.append(data['Name'])
                store.append(data['AddressLine1'])
                store.append(data['City'])
                store.append(data['StateProvince'])
                store.append(data['ZipPostalCode'])
                store.append("CA")
                store.append(data['StoreID'])
                store.append(data['Phone'])
                store.append("liquordepot")
                store.append(data['Latitude'])
                store.append(data['Longitude'])
                store.append("<INACCESSIBLE>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    # write_output(data)

scrape()
