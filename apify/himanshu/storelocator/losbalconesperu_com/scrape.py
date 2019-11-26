import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import unicodedata

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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://losbalconesperu.com"
    r = requests.get("http://losbalconesperu.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':'location-content-holder'}):
        geo_location = location.find("a")["href"]
        location_request = requests.get(location.find_all("a")[1]["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{'class':"contact-location"}).stripped_strings)
        store = []
        store.append("http://losbalconesperu.com")
        store.append(location.find("img")["alt"].replace("logo",""))
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(location_details[2].split(",")[1])
        store.append(location_details[3])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_soup.find("a",{"href":re.compile("tel:")})["href"].replace("tel:",""))
        store.append("<MISSING>")
        store.append(geo_location.split("/@")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1])
        store.append(" ".join(location_soup.find("div",{'class':"hours"}).stripped_strings))
        store.append(location.find_all("a")[1]["href"])
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
