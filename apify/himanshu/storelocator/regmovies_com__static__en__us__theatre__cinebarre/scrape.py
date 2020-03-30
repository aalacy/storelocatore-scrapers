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
    base_url = "https://www.regmovies.com"
    r = session.get("https://www.regmovies.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "apiSitesList = " in script.text:
            location_list = json.loads(script.text.split("apiSitesList = ")[1].split("}}]")[0] + "}}]")
            phone_request = session.get("https://www.regmovies.com" + location_list[0]["uri"],headers=headers)
            phone_soup = BeautifulSoup(phone_request.text,"lxml")
            phone = phone_soup.find("cinema-structured-data")["data-telephone"]
            for store_data in location_list:
                address = store_data["address"]["address1"]
                if store_data["address"]["address2"] != None:
                    address = address + " " + store_data["address"]["address2"]
                if store_data["address"]["address3"] != None:
                    address = address + " " + store_data["address"]["address3"]
                if store_data["address"]["address4"] != None:
                    address = address + " " + store_data["address"]["address4"]
                store = []
                store.append("https://www.regmovies.com")
                store.append(store_data['name'])
                store.append(address)
                store.append(store_data['address']["city"])
                store.append(store_data['address']["state"])
                store.append(store_data['address']["postalCode"])
                store.append("US")
                store.append(store_data['externalCode'])
                store.append(phone)
                store.append("regal")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
