import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    timestamp = datetime. now(). strftime("%m/%d/%Y, %H:%M:%S %p")
    addresses = []
    data = '{"timestamp":"'+str(timestamp)+'","radius":804679,"restaurantStatuses":["OPEN"],"conceptIds":["CMG"],"orderBy":"distance","orderByDescending":"false","pageSize":10000,"pageIndex":0,"embeds":{"addressTypes":["MAIN"],"publicPhoneTypes":["MAIN PHONE"],"realHours":"true","normalHours":"true","directions":"true","catering":"true","onlineOrdering":"true"}}' 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    base_url = "https://chipotle.com"
    r = session.post(base_url + "/api/v2.1/search",
                      data=data, headers=headers)
    data = r.json()["data"]
    for i in range(len(data)):
        store_data = data[i]
        if store_data['restaurantLocationType']=="LAB":
            continue
        store = []
        store.append("https://chipotle.com")
        store.append(store_data['restaurantName'])
        if "addressLine1" not in store_data["addresses"][0]:
            continue
        store.append(store_data["addresses"][0]["addressLine1"] + store_data["addresses"][0]["addressLine2"]
                        if "addressLine2" in store_data["addresses"][0] else store_data["addresses"][0]["addressLine1"])
        store.append(store_data['addresses'][0]["locality"])
        store.append(store_data['addresses'][0]["administrativeArea"]
                        if "administrativeArea" in store_data['addresses'][0] else "<MISSING>")
        if store_data['country']["countryCode"] not in ["CA","US"]:
            continue
        store.append(store_data['addresses'][0]["postalCode"])
        store.append(store_data['country']["countryCode"])
        store.append(store_data["restaurantNumber"])
        store.append(store_data["publicPhones"][0]["phoneNumber"])
        store.append(store_data["restaurantLocationType"])
        store.append(store_data['addresses'][0]["latitude"])
        store.append(store_data['addresses'][0]["longitude"])
        # store_hours = store_data["normalHours"]
        hours = ""
        try:
            for k in range(len(store_data["normalHours"])):
                
                hours = hours + " " + store_data["normalHours"][k]["dayOfWeek"] + " " + \
                    store_data["normalHours"][k]["openTime"] + \
                    " - " + store_data["normalHours"][k]["closeTime"]
            store.append(hours if hours != "" else "<MISSING>")
        except:
            store.append("<MISSING>")
        page_url = "https://locations.chipotle.com/" + \
            store[4].lower() + "/" + \
            " ".join(store[3].lower().split()).replace(
                " ", "-") + "/" + " ".join(store_data["addresses"][0]["addressLine1"].lower().split("#")[0].split("ste")[0].split(",")[0].split("unit")[0].split()).replace(" ", "-").replace("-bldg-f", "").strip().replace(".", "").replace('---','-').strip()
        store.append(page_url)
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

