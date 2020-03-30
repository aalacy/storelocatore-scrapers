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
    base_url = "https://valentinos.com"
    r = session.get("https://valentinos.com/locations/?pn=all")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class": "location_container"}):
        name = location.find('h2').text
        phone = location.find("a",{'class':"phone"}).text
        address = list(location.find("div",{'class':'address float_left'}).stripped_strings)
        hours = list(location.find("div",{'class':'float_left hours'}).stripped_strings)
        store = []
        store.append("https://valentinos.com")
        store.append(name)
        store.append(" ".join(address[0:-2]))
        store.append(address[-2].split(",")[0])
        store.append(address[-2].split(",")[1])
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone != "" else "<MISSING>")
        store.append("valentino's")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append(" ".join(hours).replace("–","-"))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
