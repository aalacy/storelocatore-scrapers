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
    base_url = "https://slaters5050.com"
    r = requests.get("https://slaters5050.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    addresses = []
    for location in soup.find_all("li",{'class':re.compile("menu-item menu-item-type-post_type menu-item-object-locations")}):
        location_request = requests.get(location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("main",{'role':"main"}).find("h1").text.strip()
        address = list(location_soup.find("p",{'class':"address"}).stripped_strings)
        if len(address[1].split(",")) != 2:
            address[0] = " ".join(address[0:2])
            del address[1]
        if address[0] in addresses:
            continue
        addresses.append(address[0])
        hours = " ".join(list(location_soup.find("div",{'class':"hours"}).stripped_strings))
        phone = location_soup.find("p",{'class':"phone"}).text.strip()
        store = []
        store.append("https://slaters5050.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[1])
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("slater's 50/50")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
