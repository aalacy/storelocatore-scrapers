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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://aromajoes.com"
    r = session.get("https://aromajoes.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if 'var json_markers = ' in script.text:
            location_list = json.loads(script.text.split('var json_markers = ')[1].split("}];")[0] + "}]")
            for i in range(len(location_list)):
                store_data = location_list[i]
                hours = " ".join(list(BeautifulSoup(store_data["content"],"lxml").stripped_strings))  
                store = []
                store.append("https://aromajoes.com")
                store.append(store_data["title"])
                store.append(store_data["address"].split("-")[1])
                store.append(store_data["address"].split("-")[0].split(",")[0])
                store.append(store_data["state_code"])
                store.append(store_data["zip_code"])
                store.append("US")
                store.append(store_data["store_no"])
                store.append(store_data["phone"] if store_data["phone"] != "Comin' Soon!" else "<MISSING>")
                store.append("aroma joe's")
                store.append(store_data['latitude'])
                store.append(store_data['longitute'])
                store.append(hours.replace("–","-").replace("\xa0"," ") if hours != "" else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
