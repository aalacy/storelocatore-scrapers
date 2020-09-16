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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://myfavoritemuffin.com"
    base_link = "https://myfavoritemuffin.com/Umbraco/Api/LocationsApi/GetNearbyLocations?latitude=40.73&longitude=-73.5&maxResults=100000&maxDistance=1000000"
    r = session.get(base_link,headers=headers)
    return_main_object = []
    for store_data in r.json():
        store = []
        store.append("https://myfavoritemuffin.com")

        try:
            street_address = (store_data["Address1"] + " " + store_data["Address2"]).strip()
        except:
            continue

        try:
            link = store_data["Links"][0]["Url"]
            req = session.get(link,headers=headers)
            base = BeautifulSoup(req.text,"lxml")
            try:
                hours = base.find(id="hours-list").text.strip().replace("\t","").replace("\r\n","").replace("\n"," ")
                hours_of_operation = (re.sub(' +', ' ', hours)).strip()
            except:
                hours_of_operation = '<MISSING>'
        except:
            link = base_link
        store.append(link)
        store.append(store_data["Name"])
        store.append(street_address)
        store.append(store_data["Locality"])
        store.append(store_data["Region"])
        store.append(store_data["PostalCode"])
        store.append("US")
        store.append(store_data["ID"])
        store.append(store_data["Phone"])
        store.append('<MISSING>')
        store.append(store_data["Latitude"])
        store.append(store_data["Longitude"])
        store.append(hours_of_operation)

        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
