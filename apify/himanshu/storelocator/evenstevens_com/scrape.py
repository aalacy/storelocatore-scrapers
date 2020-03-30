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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    base_url = "https://evenstevens.com"
    r = session.get("https://evenstevens.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for state in soup.find("ul",{'class':"w-nav-list level_2"}).find_all("a"):
        state_request = session.get(state["href"],headers=headers)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        name = list(state_soup.find("div",{'class':"w-tabs-list-h"}).stripped_strings)
        for location in state_soup.find("div",{'class':"w-tabs-sections"}).find_all("div",{"class":"w-tabs-section"}):
            address = list(location.find("p").stripped_strings)
            phone = location.find_all("p")[1].text.strip()
            hours = " ".join(list(location.find_all("p")[2].stripped_strings))
            store_zip_split = re.findall("([0-9]{5})",location.find("a",text=re.compile("GET DIRECTIONS"))["href"])
            if store_zip_split:
                store_zip = store_zip_split[-1]
            else:
                store_zip = "<MISSING>"
            store = []
            store.append("https://evenstevens.com")
            store.append(name[0])
            del name[0]
            store.append(address[0])
            store.append(address[1].split(",")[0])
            store.append(address[1].split(",")[1])
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours.replace("–","-") if hours else "<MISSING>")
            store.append(state["href"])
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()