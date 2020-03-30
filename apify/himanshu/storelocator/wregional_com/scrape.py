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
    base_url = "https://www.wregional.com"
    r = session.get(base_url+"/main/physician-locator?atoz=1")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('main',{"id":'inside-page'}).find('div',{"class":"page-content"}).find_all('div',{"class":"info"})
    for dt in main:
        loc=list(dt.stripped_strings)
        store=[]
        if len(loc)==15:
            store.append(base_url)
            store.append(loc[2])
            store.append(loc[4])
            store.append(loc[6])
            store.append(loc[8])
            store.append(loc[10])
            store.append("US")
            store.append("<MISSING>")
            store.append(loc[12])
            store.append(loc[14])
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
        else:
            if "Office Name" in loc[1]:
                store.append(base_url)
                store.append(loc[2])
                store.append(loc[4])
                store.append(loc[6])
                store.append(loc[8])
                store.append(loc[10])
                store.append("US")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(loc[12])
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
            else:
                store.append(base_url)
                store.append("<MISSING>")
                store.append(loc[2])
                store.append(loc[4])
                store.append(loc[6])
                store.append(loc[8])
                store.append("US")
                store.append("<MISSING>")
                store.append(loc[10])
                store.append(loc[12])
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
