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
    base_url = "https://www.starwoodhotels.com"
    r = requests.get("https://le-meridien.marriott.com/hotel-directory/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "window.MARRIOTT_GEO_DATA" in script.text:
            location_list = json.loads(script.text.split("window.MARRIOTT_GEO_DATA = ")[1].split("}};")[0] + "}}")["properties"]
            for key in location_list:
                current_store = location_list[key]
                store = []
                store.append("https://le-meridien.marriott.com")
                store.append(current_store["name"])
                store.append(current_store["address"])
                store.append(current_store["city"] if current_store["city"] != None and current_store["city"] != "" else "<MISSING>")
                store.append(current_store["state"] if current_store["state"] != None and current_store["state"] != "" else "<MISSING>")
                store.append(current_store["zipcode"])
                store.append(current_store["country"])  
                store.append("<MISSING>")
                store.append(current_store["phone"])
                store.append("le meridien")
                store.append(current_store["latitude"])
                store.append(current_store["longitude"])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
