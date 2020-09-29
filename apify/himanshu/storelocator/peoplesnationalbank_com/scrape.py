import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import html5lib
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.peoplesnationalbank.com"
    r = session.get("https://www.peoplesnationalbank.com/about-us/locations.html",headers=headers)
    soup = BeautifulSoup(r.text,"html5lib")
    return_main_object = []
    hours_location = {}
    for location in soup.find_all("li",{"class":re.compile("loc")}):
        address = location['data-address1']
        hours = " ".join(list(location.find("div",{'class':"hours"}).stripped_strings))
        hours_location[address] = hours
    for script in soup.find_all("script"):
        if "var gMapLocations = " in script.text:
            location_list = json.loads(script.text.split('var gMapLocations = ')[1].split("}];")[0] + "}]")
            for store_data in location_list:
                store = []
                store.append("https://www.peoplesnationalbank.com")
                store.append(store_data["name"].strip())
                store.append(store_data["address"].replace(str(store_data["zipcode"]),"").strip())
                store.append(store_data["city"])
                store.append(store_data["state"])
                store.append(store_data["zipcode"])
                store.append("US")
                store.append(store_data["filterClass"].split("location")[1])
                store.append(store_data["phones"][0].split(": ")[1] if store_data["phones"] != [] else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data['latitude'])
                store.append(store_data['longitude'])               
                store.append(hours_location[store_data["address"].replace(str(store_data["zipcode"]),"")[:-1]].replace("Lobby Hours","").replace(" By Appointment","<MISSING>").strip())
                store.append("https://www.peoplesnationalbank.com/connect/location-details.html?id="+str(store_data["filterClass"].split("location")[1]))
                return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
