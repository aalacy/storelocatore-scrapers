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
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = session.get("http://aerosportsparks.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    location_url = []
    for location in soup.find("div",{'class':"mpfy-map-canvas"}).find_all("a"):
        if location["href"] == "#":
            continue
        location_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        location_request = session.get(location["href"],headers=location_headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{"class":'mpfy-p-entry'}).stripped_strings)
        name =  location_soup.find("h1").text.strip()
        geo_location = location_soup.find("a",text="Directions to this location")["href"]
        store_zip_split = re.findall("([0-9]{5})",location_details[1])
        if store_zip_split:
            store_zip = store_zip_split[0]
        else:
            store_zip = "<MISSING>"
        state_split = re.findall("([A-Z]{2})",location_details[1])
        if state_split:
            state = state_split[0]
        else:
            state = "<MISSING>"
        store = []
        store.append("http://aerosportsparks.com")
        store.append(name)
        store.append(location_details[0])
        store.append(name.replace("Aerosports ","").split(",")[0])
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append(location["data-id"])
        store.append(location_details[-1])
        store.append("<MISSING>")
        store.append(geo_location.split("=")[-1].split(",")[0])
        store.append(geo_location.split("=")[-1].split(",")[1])
        if location_soup.find("a",{"class":"mpfy-p-color-accent-color"}):
            hours_request = session.get(location_soup.find("a",{"class":"mpfy-p-color-accent-color"})["href"] + "/contact",headers=headers)
            hours_soup = BeautifulSoup(hours_request.text,"lxml")
            store.append(" ".join(list(hours_soup.find_all("div",{"class":'fl-rich-text'})[-1].stripped_strings)))
            store.append(location_soup.find("a",{"class":"mpfy-p-color-accent-color"})["href"])
        else:
            store.append("<MISSING>")
            store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()