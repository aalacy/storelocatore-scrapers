import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib3.exceptions import InsecureRequestWarning
import unicodedata

requests.packages.urllib3.disable_warnings()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_main_object = []
    base_url = "https://ravecinemas.com"
    r = requests.get("https://ravecinemas.com/full-theatre-list",headers=headers,verify=False)
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find("div",{"class":"columnList wide"}).find_all("a"):
        # print(base_url + location["href"])
        location_request = requests.get(base_url + location["href"],headers=headers,verify=False)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("div",{"class":"theatreMap"}) == None:
            continue
        geo_location = location_soup.find("div",{"class":"theatreMap"}).find("img")["data-src"]
        for script in location_soup.find_all("script",{"type":"application/ld+json"}):
            try:
                location_details = json.loads(script.text)
                if "screenCount" in location_details:
                    break
            except:
                continue
        address = location_details["address"][0]
        store = []
        store.append("https://ravecinemas.com")
        store.append(location_details["name"])
        if "NOW CLOSED".lower() in store[-1].lower():
            continue
        store.append(address["streetAddress"])
        store.append(address["addressLocality"])
        store.append(address["addressRegion"])
        store.append(address["postalCode"])
        store.append(address["addressCountry"])
        store.append("<MISSING>")
        store.append(location_details["telephone"] if location_details["telephone"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(geo_location.split("&pp=")[1].split(",")[0] if geo_location.split("&pp=")[1].split(",")[0] else "<MISSING>" )
        store.append(geo_location.split("&pp=")[1].split(",")[1].split("&")[0] if geo_location.split("&pp=")[1].split(",")[1].split("&")[0] else "<MISSING>")
        store.append("<MISSING>")
        store.append(base_url + location["href"])
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()