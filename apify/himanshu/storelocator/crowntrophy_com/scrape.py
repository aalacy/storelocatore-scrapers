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
    base_url = "https://www.crowntrophy.com"
    r = session.get(base_url + "/grid/index/index")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object  = []
    for store_data in soup.find_all("div",{"class":"stores-list-item"}):
            store = []
            store.append("https://www.crowntrophy.com")
            store.append(store_data['data-city'])
            store.append(store_data["data-address"])
            store.append(store_data['data-city'])
            store.append(store_data['data-state'])
            if "NJ" in store[-1]:
                store[-1] = "NJ"
            store.append(store_data["data-zip"])
            store.append("US")
            store.append(store_data['data-store'])
            store.append(store_data['data-phone'])
            store.append("crown trophy")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            location_request = session.get(base_url + store_data.find("a")["href"])
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if location_soup.find("div",{"class":"flex_start flex_between"}) != None:
                store.append(" ".join(list(location_soup.find("div",{"class":"flex_start flex_between"}).find_all("div",recursive=False)[1].stripped_strings)))
            else:
                store.append("<MISSING>")
            if store[-1] == "":
                store[-1] = "<MISSING>"
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
