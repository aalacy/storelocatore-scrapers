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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://tomsfamous.com"
    r = session.get("https://tomsfamouscom.wpcomstaging.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_url = []
    addresses = []
    for location in soup.find_all("div",{'class':"elementor-row"}):
        if location.find("iframe") == None:
            continue
        location_details = list(location.find("h2").stripped_strings)
        if "OPENING SOON" in location_details[-1]:
            continue
        store_zip_split = re.findall(r'([0-9]{5})',location_details[2])
        if store_zip_split:
            store_zip = store_zip_split[0]
        state_split = re.findall(" ([A-Z]{2}) ",location_details[2])
        if state_split:
            state = state_split[0]
        city = location_details[2].split(",")[0]
        hours = ""
        for i in range(len(location_details)):
            if location_details[i] == "Hours":
                hours = " ".join(location_details[i+1:])
        store = []
        store.append("https://tomsfamous.com")
        store.append(location_details[0])
        store.append(location_details[1])
        if store[-1] in addresses:
            continue
        addresses.append(store[-1])
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append(location_details[0].split(" ")[-1])
        store.append(location_details[3] if location_details[3] != "Hours" else "<MISSING>")
        store.append("tom's")
        geo_request = session.get(location.find("iframe")["src"],headers=headers)
        geo_soup = BeautifulSoup(geo_request.text,"lxml")
        for script in geo_soup.find_all("script"):
            if "initEmbed" in script.text:
                lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]
        store.append(lat)
        store.append(lng)
        store.append(hours if hours else "<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()