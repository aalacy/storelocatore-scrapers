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
    base_url = "https://rotolos.com"
    r = session.get("https://rotolos.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("select",{'id':"restaurant-select"}).find_all("option"):
        if "loc_link" not in location.attrs:
            continue
        location_request = session.get(location["loc_link"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        current_location = location_soup.find("div",{'class':'marker'})
        location_details = list(current_location.stripped_strings)
        if len(location_details) == 4:
            location_details[0] = " ".join(location_details[0:2])
            del location_details[1]
        hours = " ".join(list(location_soup.find("div",{'id':'location-hours'}).stripped_strings)[1:]).strip()
        store = []
        store.append("https://rotolos.com")
        store.append(location_soup.find("h1").text)
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[1].split(" ")[-2])
        store.append(location_details[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[-1])
        store.append("stoney river")
        store.append(current_location["data-lat"])
        store.append(current_location["data-lng"])
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
