import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    base_url = "https://www.ethanallen.com"
    data = 'countryCode=US'
    r = session.post("https://www.ethanallen.com/on/demandware.store/Sites-ethanallen-us-Site/en_US/Stores-GetStatesByCountry",headers=headers,data=data)
    return_main_object = []
    state_data = r.json()["states"]
    for state in state_data:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        state_request = session.get("https://www.ethanallen.com/on/demandware.store/Sites-ethanallen-us-Site/en_US/Stores-GetStoreListByCountryAndState?countryCode=US&stateCode=" + state["code"],headers=headers)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        for location in state_soup.find_all("div",{'class':"store"}):
            name = location.find("h3").text
            address = list(location.find("p",{'class':"address"}).stripped_strings)
            store_id = location["data-id"]
            phone = location["data-phone"]
            hours = " ".join(list(location.find_all("li")[1].stripped_strings))
            store = []
            store.append("https://www.ethanallen.com")
            store.append(name)
            store.append(address[0])
            store.append(address[1].split(",")[0])
            store.append(address[1].split(",")[1])
            store.append(address[1].split(",")[2])
            store.append("US")
            store.append(store_id)
            store.append(phone if phone != "" else "<MISSING>")
            store.append("ethan allen")
            store.append(location["data-lat"])
            store.append(location["data-lng"])
            store.append(hours)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
