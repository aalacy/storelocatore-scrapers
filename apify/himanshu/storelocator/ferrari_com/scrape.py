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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://ferrari.com"
    r = session.get("https://store.ferrari.com/en-us/store-locator#search/country/us",headers=headers)
    header_id = r.text.split("storeLocatorConfig.APIConnectClientID = ")[1].split(";")[0].replace("'","")
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "X-IBM-Client-Id": header_id
    }
    r = session.get("https://ecomm.ynap.biz/os/os1//wcs/resources/store/ferrari_US/storelocator/boutiques?pageSize=100",headers=headers)
    location_list = r.json()["data"]
    return_main_object = []
    for store_data in location_list:
        address = store_data["address"]
        if address["countryCode"] not in ("US","CA"):
            continue
        street_address = address["line1"].split(address["city"])[0].replace("-","")
        store = []
        store.append("https://ferrari.com")
        store.append(store_data["storeName"])
        store.append(street_address)
        store.append(address["city"])
        store.append(address["state"])
        store.append(address["postCode"])
        store.append(address["countryCode"])
        store.append(store_data["storeNumber"])
        store.append(address["phone1"] if address['phone1'] else "<MISSING>")
        store.append(store_data["attributes"][0]["values"][0]["value"])
        store.append(store_data["spatialData"]["latitude"])
        store.append(store_data["spatialData"]["longitude"])
        hours = ""
        store_hours = store_data["openingTimes"]
        days = {1:"Monday",2:"Tuesday",3:"Wednesday",4:"Thursday",5:"Friday",6:"Saturday",7:"Sunday"}
        for hour in store_hours:
            hours = hours + " " + days[hour["dayNumber"]] + " " + hour["slots"][0]["openTime"] + " - " + hour["slots"][0]["closeTime"]
        store.append(hours if hours != "" else "<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
