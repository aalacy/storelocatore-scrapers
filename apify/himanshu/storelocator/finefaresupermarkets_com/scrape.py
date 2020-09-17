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
    base_url = "http://finefaresupermarkets.com/locations.aspx"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main=soup.find("table",{"class":"style17"}).find_all("tr")
    del main[0]
    for location in main:
        location_address=list(location.stripped_strings)
        store = []
        store.append("http://finefaresupermarkets.com")
        store.append("<MISSING>")
        store.append(location_address[0])
        store.append(location_address[1])
        store.append(location_address[2])
        store.append("<MISSING>")
        store.append("US")  
        store.append("<MISSING>")
        store.append(location_address[3])
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
