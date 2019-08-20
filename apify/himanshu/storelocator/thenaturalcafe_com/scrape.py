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
    base_url = "http://thenaturalcafe.com"
    r = requests.get("http://thenaturalcafe.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"location"}):
        name = location.find("h2").text.strip()
        address = list(location.find("p").stripped_strings)
        phone = list(location.find_all("p")[1].stripped_strings)[1]
        hours = list(location.find_all("p")[2].stripped_strings)[1]
        if len(address) == 3:
            address[0] = " ".join(address[0:2])
            del address[1]
        geo_location = location.find("iframe")["src"]
        store = []
        store.append("http://thenaturalcafe.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[1])
        store.append(address[1].split(",")[1].split(" ")[-1] if len(address[1].split(",")[1].split(" ")[-1]) == 5 else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("the natural cafe")
        if "!2d" in geo_location and "!3d" in geo_location:
            store.append(geo_location.split("!3d")[1].split("!")[0])
            store.append(geo_location.split("!2d")[1].split("!")[0])
        elif "&ll=" in geo_location:
            store.append(geo_location.split("&ll=")[1].split(",")[0])
            store.append(geo_location.split("&ll=")[1].split(",")[0].split("&")[0])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
