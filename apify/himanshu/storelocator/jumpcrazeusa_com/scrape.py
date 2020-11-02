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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://jumpcrazeusa.com"
    r = session.get(base_url+"/casper-wyoming/")
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    main=soup.find('div',{"class":"b2b-location-items"}).find('ul').find_all('li')
    for ltag in main:
        loc=list(ltag.stripped_strings)
        name=loc[0]
        address=loc[1]
        ct=loc[2].split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        phone=loc[6]
        del loc[0:7]
        del loc[-1]
        store = []
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append('US')
        store.append("<MISSING>")
        store.append(phone)
        store.append("jumpcrazeusa")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(' '.join(loc))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
