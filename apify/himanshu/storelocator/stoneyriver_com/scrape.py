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
    base_url = "https://stoneyriver.com"
    r = requests.get("https://stoneyriver.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"location-details"}):
        address = list(location.find("p").stripped_strings)
        if len(address) == 4:
            address[0] = " ".join(address[0:2])
            del address[1]
        if len(address[1].split(",")) != 2:
            address = list(location.find_all("p")[-1].stripped_strings)
        address[1] = address[1].replace("\t"," ")
        address[0] = address[0].replace("\t"," ")
        if "       " in address[1]:
            address[0] = address[0] + address[1].split("       ")[0]
            address[1] = address[1].split("       ")[1]
        phone = list(location.find_all("p")[1].stripped_strings)
        hours = " ".join(list(location.find("div",{'class':'hours'}).stripped_strings)[1:]).strip()
        store = []
        store.append("https://stoneyriver.com")
        store.append(address[1].split(",")[0])
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(" ".join(address[1].split(",")[1].split(" ")[1:-1]))
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[-1] if len(phone) == 3 else "<MISSING>")
        store.append("stoney river")
        if location.find("a",{'href':re.compile("/@")}) != None:
            geo_location = location.find("a",{'href':re.compile("/@")})["href"]
            store.append(geo_location.split("/@")[1].split(",")[0])
            store.append(geo_location.split("/@")[1].split(",")[1])
        elif location.find("a",{'href':re.compile("ll=")}) != None:
            geo_location = location.find("a",{'href':re.compile("ll=")})["href"]
            store.append(geo_location.split("ll=")[1].split(",")[0])
            store.append(geo_location.split("ll=")[1].split(",")[1].split("&")[0])
        else:
            store.append("<MISSING>")
            store.append("<MISSING>")
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
