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
    base_url = "http://www.jinkys.com"
    r = requests.get("http://www.jinkys.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("ul",{'class':"dropdown-menu"}).find_all("a"):
        location_request = requests.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("td").stripped_strings)
        if len(location_details[0]) == 1:
            location_details[0] = "".join(location_details[0:2])
            del location_details[1]
        if location_details[1] == "Â":
            del location_details[1]
        if location_details[1][-1] == "Â":
            location_details[1] = location_details[1][:-2]
        location_details[0] = location_details[0].replace("\x80","").replace("\x99","")
        name = str(location_details[0]).replace("â","'")
        street = location_details[1].split(",")[0].replace(name.replace("Jinky's ",""),"")
        city = str(location_details[0]).replace("â","'").replace("Jinky's ","")
        if len(location_details[1].split(",")[-1].split(" ")) >= 2 and len(location_details[1].split(",")[-1].split(" ")[1]) == 2:
            state = location_details[1].split(",")[-1].split(" ")[1]
        else:
            state = "<MISSING>"
        if len(location_details[1].split(",")[-1].split(" ")[-1]) == 5:
            zip_code = location_details[1].split(",")[-1].split(" ")[-1]
        else:
            zip_code = "<MISSING>"
        store = []
        store.append("http://www.jinkys.com")
        store.append(name)
        store.append(street.replace("\xa0","").replace("Â",""))
        store.append(city)
        store.append(state)
        store.append(zip_code)
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[4])
        store.append("jinky's")
        geo_lcoation = location_soup.find_all("iframe")[-1]["src"]
        store.append(geo_lcoation.split("!3d")[1].split("!")[0])
        store.append(geo_lcoation.split("!2d")[1].split("!")[0])
        store.append(location_details[8] if "Get Directions" not in location_details[8]else location_details[7])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
