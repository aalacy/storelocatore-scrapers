import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
def handle_store(store_data,country_code):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    store = []
    store.append("https://mamadelucaspizza.com")
    store.append(store_data["name"])
    store.append(store_data["address"] + " " + store_data["address2"] if store_data["address2"] != None else store_data["address"])
    store.append(store_data["city"])
    if country_code == "US":
        store.append(store_data["state"])
    else:
        store.append(store_data["province"])
    store.append(store_data["zip"] if store_data["zip"] != None else "<MISSING>")
    store.append(country_code)
    store.append(store_data["id"])
    store.append(store_data["phone"])
    store.append("mama deluca's pizza")
    store.append("<MISSING>")
    store.append("<MISSING>")
    hours = ""
    location_request = requests.get(store_data["link"],headers=headers)
    location_soup = BeautifulSoup(location_request.text,"lxml")
    if location_soup.find("div",{'class':"hours"}) == None:
        store.append("<MISSING>")
    else:
        store.append(" ".join(list(location_soup.find("div",{'class':"hours"}).stripped_strings)))
    return store

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://mamadelucaspizza.com"
    r = requests.get("https://mamadelucaspizza.com/wp-json/mdp/v1/states",headers=headers)
    data = r.json()
    return_main_object = []
    for state in data:
        state_request = requests.get("https://mamadelucaspizza.com/wp-json/mdp/v1/USlocations?state=" + state,headers=headers)
        if "code" in state_request.json():
            continue
        stores = state_request.json()
        for store_data in stores:
            store = handle_store(store_data,"US")
            if store[2] == "COMING SOON!":
                continue
            return_main_object.append(store)
    r = requests.get("https://mamadelucaspizza.com/wp-json/mdp/v1/globallocations?country=CA",headers=headers)
    data = r.json()
    for store_data in data:
        store = handle_store(store_data,"CA")
        if store[2] == "COMING SOON!":
                continue
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
