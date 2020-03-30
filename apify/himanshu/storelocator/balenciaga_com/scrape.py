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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.balenciaga.com"
    r = session.get("https://www.balenciaga.com/experience/us/?yoox_storelocator_action=true&action=yoox_storelocator_get_all_stores",headers=headers)
    data = r.json()
    return_main_object = []
    for store_data in data:
        store = []
        if "location" not in store_data:
            continue
        if store_data["location"]["country"]["name"] != "USA" and store_data["location"]["country"]["name"] != "Canada":
            continue
        store.append("https://www.balenciaga.com")
        store.append(store_data["post_title"])
        store.append(store_data["wpcf-yoox-store-address"].split(",")[0].replace(store_data["location"]["city"]["name"],"").replace("\r"," ").replace("\n"," ").replace("  "," "))
        store.append(store_data["location"]["city"]["name"])
        if store_data["wpcf-yoox-store-country-iso"] == "US":
            store.append(store_data["wpcf-yoox-store-address"].replace("\n"," ").split(" ")[-2].replace("\n"," "))
            store.append(store_data["wpcf-yoox-store-address"].replace("\n"," ").replace("\r","").split(" ")[-1])
        else:
            store.append(store_data["wpcf-yoox-store-address"].replace("\n"," ").split(" ")[-3].replace("\n"," "))
            store.append(" ".join(store_data["wpcf-yoox-store-address"].replace("\n"," ").split(" ")[-2:]))
        store[2] = store[2].replace(store[4],"").replace(store[5],"").replace("  ","").replace("\xa0","")
        store.append(store_data["wpcf-yoox-store-country-iso"])
        store.append(store_data["ID"])
        store.append(store_data["wpcf-yoox-store-phone"].replace("\xa0","") if "wpcf-yoox-store-phone" in store_data else "<MISSING>")
        store.append("balenciaga")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append(" ".join(list(BeautifulSoup(store_data["wpcf-yoox-store-hours"].replace("\r"," ").replace("\n"," "),"lxml").stripped_strings)) if "wpcf-yoox-store-hours" in store_data else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
