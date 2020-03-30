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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://malbeccuisine.com"
    r = session.get("http://malbeccuisine.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("ul",{'class':"location_modal"}).find_all("a"):
            location_request = session.get(base_url + location["href"],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            location_details = list(location_soup.find("section",{"class":"contact_info"}).find("ul").stripped_strings)
            store = []
            store.append("http://malbeccuisine.com")
            store.append(location.text)
            store.append(location_details[0].split("|")[0])
            store.append(location_details[0].split("|")[1].split(",")[0])
            store.append(location_details[0].split("|")[1].split(",")[1].split(" ")[-2])
            store.append(location_details[0].split("|")[1].split(",")[1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(location_details[1])
            store.append("malbec argentinean cuisine")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(" ".join(location_soup.find("div",{'class':"hours"}).stripped_strings))
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
