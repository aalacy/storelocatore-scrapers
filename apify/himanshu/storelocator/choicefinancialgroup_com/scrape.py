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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://choicefinancialgroup.com"
    r = session.get("https://bankwithchoice.com/contact/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"col-lg-3 col-md-6 bucket-content"}):
        location_details = list(location.find("p").stripped_strings)
    
        for i in range(len(location_details)):
            if "Hours" in location_details[i] or "Lobby" in location_details[i]:
                hours = " ".join(location_details[i:]).split("Night")[0]
                break
        store = []
        store.append("https://choicefinancialgroup.com")
        store.append(location.find("a").text.strip())
        store.append(location_details[0].split("–")[0].strip())
        store.append(location_details[0].split("–")[1].split(",")[0].strip())
        store.append(location_details[0].split("–")[1].split(",")[1].split()[0])
        store.append(location_details[0].split("–")[1].split(",")[1].split()[1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[2])
        store.append("<MISSING>")
        if location.find("a") != None:
            geo_location = location.find("a")["href"]
            store.append(geo_location.split("/@")[1].split(",")[0] if len(geo_location.split("/@")) == 2 else "<MISSING>")
            store.append(geo_location.split("/@")[1].split(",")[1] if len(geo_location.split("/@")) == 2 else "<MISSING>")
        else:
            store.append("<MISSING>")
            store.append("<MISSING>")
        store.append(hours)
        store.append("https://bankwithchoice.com/contact/locations/")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
