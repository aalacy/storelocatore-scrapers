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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.eastcoastsalon.com"
    r = session.get("https://www.eastcoastsalon.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    hours = " ".join(list(soup.find("div",{'class':"hours"}).stripped_strings))
    return_main_object = []
    for script in soup.find_all("script"):
        if "var locations = [" in script.text:
            location_list = json.loads( "[" + script.text.split("var locations = [")[1].split("];")[0].replace("'",'"') + "]")
            for store_data in location_list:
                store = []
                store.append("https://www.eastcoastsalon.com")
                store.append(store_data[0])
                store.append(BeautifulSoup(store_data[1],"lxml").get_text())
                store.append(store_data[0].split(",")[0])
                store.append(store_data[0].split(",")[-1])
                store.append(store_data[2].split(" ")[-1])
                store.append("US")
                store.append(store_data[-1])
                store.append(store_data[3])
                store.append("east coast salon services")
                store.append(store_data[-3])
                store.append(store_data[-2])
                store.append(hours)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
