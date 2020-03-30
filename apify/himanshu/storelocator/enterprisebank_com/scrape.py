import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

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
    base_url = "https://www.enterprisebank.com"
    r = session.get("https://www.enterprisebank.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_locations = {}
    for location in soup.find_all("div",{"class":'geolocation'}):
        name = list(location.stripped_strings)[0]
        geo_locations[name] = [location["data-lat"],location["data-lng"]]
    for location in soup.find_all("div",{'class':"views-row"}):
        location_details = list(location.stripped_strings)
        if len(location_details[2].split(",")) == 1:
            location_details[1] = location_details[1:3]
            del location_details[2]
        address = location_details[2].replace("\n"," ")
        store = []
        store.append("https://www.enterprisebank.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(address.split(",")[0])
        store.append(address.split(" ")[-13])
        store.append(address.split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[3])
        store.append("enterprise bank")
        store.append(geo_locations[location_details[0]][0])
        store.append(geo_locations[location_details[0]][1])
        store.append(" ".join(location_details[4:]).replace("\xa0"," "))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
