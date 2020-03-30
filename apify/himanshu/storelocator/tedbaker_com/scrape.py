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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.tedbaker.com"
    r = session.get("https://www.tedbaker.com/us/json/stores/for-country?isocode=US",headers=headers)
    data = r.json()["data"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        raw_address = ""
        address = store_data["address"]
        if "line1" in address:
            raw_address = raw_address + address["line1"] + " "
        if "line2" in address:
            raw_address = raw_address + address["line2"] + " "
        if "line3" in address:
            raw_address = raw_address + address["line3"] + " "
        if "postalCode" in address:
            raw_address = raw_address + address["postalCode"]
        if "line2" not in store_data["address"]:
                continue
        store.append("https://www.tedbaker.com")
        store.append(store_data["displayName"])
        # print(store)
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append(store_data["address"]["country"]["isocode"])
        store.append(store_data["openingHours"]["code"].replace("US",""))
        store.append(store_data["address"]["phone"] if "phone" in store_data["address"] and store_data["address"]["phone"] != "" and store_data["address"]["phone"] != None else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["geoPoint"]["latitude"])
        store.append(store_data["geoPoint"]["longitude"])
        hours = ""
        if "openingHours" in store_data:
            store_hours = store_data["openingHours"]["weekDayOpeningList"]
            for k in range(len(store_hours)):
                if store_hours[k]["closed"] == True:
                    hours = hours + " closed " + store_hours[k]["weekDay"]
                else:
                    hours = hours + " " + store_hours[k]["weekDay"] + " open time " + store_hours[k]["openingTime"]["formattedHour"] + " close time " + store_hours[k]["closingTime"]["formattedHour"]
        store.append(hours if hours != "" else "<MISSING>")
        store.append("<MISSING>")
        store.append(raw_address)
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = store[i].replace("–","-")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
