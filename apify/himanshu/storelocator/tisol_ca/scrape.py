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
    base_url = "https://tisol.ca"
    r = session.get("https://tisol.ca/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"et_pb_map_pin"}):
        name = location.find("h3").text
        location_details = list(location.find("p").stripped_strings)[:-1]
        store = []
        store.append("https://tisol.ca")
        store.append(name)
        store.append(location_details[0].split(",")[0])
        store.append(location_details[0].split(",")[1])
        store.append("<MISSING>")
        for location1 in soup.find_all("div",{"class":"et_pb_module"}):
            if location1.find('h5') == None:
                continue
            if name == location1.find("h5").text:
                location_details[0] = list(location1.find("p").stripped_strings)[1]
        store.append(location_details[0].split(",")[-1][1:])
        store.append("CA")
        store.append("<MISSING>")
        store.append(location_details[1])
        store.append("tisol")
        store.append(location["data-lat"])
        store.append(location["data-lng"])
        store.append(" ".join(location_details[2:]))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
