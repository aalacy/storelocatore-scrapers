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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","row_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.rockfish.com"
    r = session.get("http://www.rockfish.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if '"locations":' in script.text:
            location_list = json.loads(script.text.split('"locations":')[1].split("}]")[0] + "}]")
            for i in range(len(location_list)):
                store_data = location_list[i]
                location_details = list(BeautifulSoup(store_data["description"],"lxml").stripped_strings)
                for k in range(len(location_details)):
                    if location_details[k] == "Menu":
                        location_details = location_details[:k]
                        break
                for k in range(len(location_details)):
                    if "(" in location_details[k] and ")" in location_details[k]:
                        phone = location_details[k]
                    if "Hours" in location_details[k]:
                        hours = " ".join(location_details[k+1:])
                zip_codes = re.findall(r'\d+', store_data["address"])
                for k in range(len(zip_codes)):
                    if len(str(zip_codes[k])) == 5:
                        store_zip = zip_codes[k]
                state = BeautifulSoup(store_data["address"],"lxml").text.replace("\n"," ").split(" ")
                for k in range(len(state)):
                    if len(str(state[k])) == 2:
                        store_state = state[k]
                store = []
                store.append("http://www.rockfish.com")
                store.append(store_data["title"])
                store.append("<INACCESSIBLE>")
                store.append("<INACCESSIBLE>")
                store.append(store_state)
                store.append(store_zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("rock fish")
                store.append(store_data['latitude'])
                store.append(store_data['longitude'])
                store.append(hours if hours != "" else "<MISSING>")
                store.append(BeautifulSoup(store_data["address"],"lxml").text.replace("\n"," "))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
