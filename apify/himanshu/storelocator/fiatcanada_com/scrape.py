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
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.fiatcanada.com"
    r = session.get("https://www.fiatcanada.com/data/dealers/expandable-radius?brand=fiat&longitude=-79.3984&latitude=43.7068&radius=100000",headers=headers)
    return_main_object = []
    location_data = r.json()["dealers"]
    for store_data in location_data:
        store = []
        store.append("https://www.fiatcanada.com")
        store.append(store_data["name"])
        store.append(store_data["address"])
        store.append(store_data["city"])
        store.append(store_data["province"])
        store.append(store_data["zipPostal"][:3] + " " + store_data["zipPostal"][3:])
        store.append("CA")
        store.append(store_data["code"])
        store.append(store_data["contactNumber"])
        store.append("fiat")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        location_request = session.get("https://www.fiatcanada.com/en/dealers/" + store_data["code"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("div",{'class':"C_DD-accordeonContent"}) == None:
            hours = "<MISSING>"
        else:
            hours = " ".join(list(location_soup.find("div",{'class':"C_DD-accordeonContent"}).stripped_strings))
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
