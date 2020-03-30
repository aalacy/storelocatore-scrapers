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
    base_url = "https://www.jysk.ca"
    r = session.get(base_url + "/jysk-locations")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "var map" in script.text:
            location_list = json.loads(script.text.split("var map = ")[1].split("({")[1].split(");")[0].split("]}},")[0].split("'markers' : ")[1] + "]}}")
            # print(json.dumps(location_list["6"],indent=4))
            for key in location_list:
                current_store = location_list[key]
                store = []
                store.append("https://www.jysk.ca")
                store.append(current_store["title"])
                store.append(BeautifulSoup(current_store["display_address"],"lxml").text)
                store.append(current_store["city"])
                store.append(current_store["state_name"])
                store.append(current_store["postcode"])
                store.append(current_store["country"])  
                store.append(current_store["warehouse_id"])
                store.append(current_store["phone"] if current_store["phone"] != None else "<MISSING>")
                store.append("jysk")
                store.append(current_store["latitude"])
                store.append(current_store["longitude"])
                location_hours = BeautifulSoup(current_store["cms_work_times"],"lxml").find_all("div",{"class":"hoursTitle"})
                hours = BeautifulSoup(current_store["cms_work_times"],"lxml").get_text().replace("Get Direction"," ").replace("\n"," ").replace("Â"," ")
                store.append(hours if hours != "" else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
