import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.obica.com"
    r = session.get("http://www.obica.com/restaurants",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("div",{'id':"usa"}).find_all("a"):
        location_request = session.get(base_url + location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        address = list(location_soup.find("div",{'id':"info"}).find("div",{'class':"info-ltext"}).stripped_strings)
        if len(address) == 3:
            address[0] = " ".join(address[0:2])
            del address[1]
        phone = location_soup.find("div",{'id':"info"}).find("a",{'href':"#"}).text
        name = location_soup.find("h1").text.strip()
        hours = " ".join(list(location_soup.find("div",{'id':"booking"}).stripped_strings))
        geo_location = location_soup.find("div",{'id':"info"}).find("a")["href"]
        address[1] = address[1].replace("\xa0"," ")
        store = []
        store.append("http://www.obica.com")
        store.append(name.replace("\xa0"," "))
        store.append(address[0])
        store.append(" ".join(address[1].split(" ")[2:]))
        store.append(address[1].split(" ")[0])
        store.append(address[1].split(" ")[1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(geo_location.split("/@")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1])
        store.append(hours.replace("\xa0"," "))
        store.append(base_url + location["href"])
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
