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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.cassanos.com"
    return_main_object=[]
    r = session.get(base_url+'/online-ordering/')
    soup=BeautifulSoup(r.text,'lxml')
    
    for dt in soup.find('article',{"class":'all-locations'}).find_all("div",{"class":"location-block"}):
        data = list(dt.stripped_strings)
        location_name = data[0]
        street_address = data[1]
        store=[]
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(location_name)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("cassanos")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("https://www.cassanos.com/online-ordering/")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
