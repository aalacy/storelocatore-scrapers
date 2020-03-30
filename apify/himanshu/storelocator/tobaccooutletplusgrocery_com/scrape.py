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
    base_url = "https://tobaccooutletplusgrocery.com"
    r = session.get("https://topg-api.azurewebsites.net/store/info",headers=headers)
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://tobaccooutletplusgrocery.com")
        store.append(store_data["name"])
        store.append(store_data["address"]["address1"] + store_data["address"]["address2"])
        store.append(store_data["address"]["city"])
        store.append(store_data["address"]["state"])
        store.append(store_data["address"]["zip"])
        store.append("US")
        store.append(str(store_data["storeNumber"]).split(".")[0])
        store.append(store_data["phone"])
        store.append("tabaco outlet plus grocery")
        store.append(store_data["lat"])
        store.append(store_data["long"])
        hours = ""
        store_hours = store_data["hours"]
        for k in range(len(store_hours)):
            hours = hours + " " + store_hours[k]["dayOfWeek"] + " open time " + store_hours[k]["openTime"] + " close time " + store_hours[k]["closeTime"]
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
