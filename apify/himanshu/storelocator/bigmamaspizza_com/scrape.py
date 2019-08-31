import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://bigmamaspizza.com"
    r = requests.get("https://big-mamas-and-papas-pizzeria-locations.brygid.online/zgrid/themes/13278/portal/carryout.jsp",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("ul",{'class':"locations-list"}).find_all("li",{'class':"location"}):
        location_details = list(location.stripped_strings)
        store = []
        store.append("https://bigmamaspizza.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(location_details[2].split(",")[1].split(" ")[-2])
        store.append(location_details[2].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[3])
        store.append("big mama's paap's pizzaria")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
