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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://foodkingcostplus.com"
    r = session.get(base_url + "/contact-us/")
    soup = BeautifulSoup(r.text,"lxml")

    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "gmpAllMapsInfo" in script.text:
            location_list = json.loads(script.text.split("gmpAllMapsInfo = ")[1].split("];")[0] + "]")[0]["markers"]
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("https://foodkingcostplus.com")
                store.append("<MISSING>")
                store.append(store_data["title"])
                cleanr = list(BeautifulSoup(store_data["description"],"lxml").stripped_strings)
                try:
                    store_address_details = []
                    store_address_details.append(store_data["address"].split(",")[0].strip())
                    store_address_details.append(store_data["address"].split(",")[1].strip())
                    store_address_details.append(store_data["address"].split(",")[2].split(" ")[1].strip())
                    store_address_details.append(store_data["address"].split(",")[2].split(" ")[2].strip())
                    store.extend(store_address_details)
                except:
                    store_address_details = []
                    store_address_details.append(store_data["description"].split("<p>")[1].split("</p>")[0].split(",")[0].strip())
                    store_address_details.append(store_data["description"].split("<p>")[1].split("</p>")[0].split(",")[1].strip())
                    store_address_details.append(store_data["description"].split("<p>")[1].split("</p>")[0].split(",")[2].split(" ")[1].strip())
                    store_address_details.append(store_data["description"].split("<p>")[1].split("</p>")[0].split(",")[2].split(" ")[2].strip())
                    store.extend(store_address_details)
                store.append("US")
                store.append(store_data["id"])
                store.append(cleanr[-1].split(":")[1].strip())
                store.append("<MISSING>")
                store.append(store_data["position"]["coord_y"])
                store.append(store_data["position"]["coord_x"])
                hours = cleanr[1].split("Hours:")[1].replace("\xa0","").strip()
                if not hours:
                    hours = cleanr[2].replace("\xa0","").strip()
                store.append(hours)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
