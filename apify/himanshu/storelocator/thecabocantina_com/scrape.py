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
    base_url = "http://thecabocantina.com"
    r = requests.get("http://thecabocantina.com/pages/locations.aspx",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("div",{'id':"content"}).find_all("a"):
        if location["href"][0] != "/":
            continue
        location_request = requests.get(base_url + location["href"])
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{'id':"left_pnl"}).stripped_strings)
        geo_location = location_soup.find("iframe")["src"]
        store = []
        store.append("http://thecabocantina.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(location_details[2].split(",")[1].split(" ")[1])
        store.append(location_details[2].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[3].replace("Phone: ",""))
        store.append("cabo cantina")
        store.append(geo_location.split("sll=")[1].split(",")[0])
        store.append(geo_location.split("sll=")[1].split(",")[0])
        store.append(" ".join(location_details[6:]))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
