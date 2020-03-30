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
    base_url = "https://www.eaglerider.com"
    r = session.get(base_url + "/locations")
    soup = BeautifulSoup(r.text,"lxml")
    scripts = soup.find_all("script")
    return_main_object = []
    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if 'data: {"non_us_locations"' in script.text:
            file1 = open("myfile1.txt","w")
            file1.write(script.text)
            location_list = json.loads(script.text.split("markers: ")[1].split("image_paths:")[0].split("}],")[0] + "}]")
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("https://www.eaglerider.com")
                store.append(store_data['name'])
                store.append(store_data["street_address"])
                store.append(store_data['city'])
                store.append(store_data['state'])
                store.append(store_data["postal_code"].strip())
                if store_data["country_name"] == "United States of America" or store_data["country_name"] == "Canada":
                    if store_data["country_name"] == "United States of America":
                        store.append("US")
                    else:
                        store.append("CA")
                else:
                    continue
                store.append(store_data['id'])
                store.append(store_data['phone'])
                store.append("eagle rider")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                store.append(" ".join(store_data["hours_of_operation"]) if "hours_of_operation" in store_data and store_data["hours_of_operation"] != ""  else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
