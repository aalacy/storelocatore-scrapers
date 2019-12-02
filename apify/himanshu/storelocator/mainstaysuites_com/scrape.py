import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import datetime
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    today = datetime.date.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    for zip_code in zips:
        base_url = "https://mainstaysuites.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
            "Origin": "https://www.choicehotels.com",
            "Referer": "https://www.choicehotels.com/mainstay",
            "Accept": "application/json, text/plain, */*",
            "adrum": "isAjax:true",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        data = "adults=1&checkInDate=" + today + "&checkOutDate=" + tomorrow + "&placeName="  + str(zip_code) + "&platformType=DESKTOP&preferredLocaleCode=en-us&ratePlanCode=RACK&ratePlans=RACK%2CPREPD%2CPROMO%2CFENCD&rateType=LOW_ALL&searchRadius=100&siteName=us&siteOpRelevanceSortMethod=ALGORITHM_B"
        r = requests.post("https://www.choicehotels.com/webapi/location/hotels",headers=headers,data=data)
        if "hotels" not in r.json():
            continue
        data = r.json()["hotels"]
        for store_data in data:
            if store_data["address"]["country"] != "US":
                continue
            store = []
            store.append("https://mainstaysuites.com")
            store.append(store_data["name"])
            address = ""
            if "line1" in store_data["address"]:
                address = address + store_data["address"]["line1"]
            if "line2" in store_data["address"]:
                address = address + store_data["address"]["line2"]
            if "line3" in store_data["address"]:
                address = address + store_data["address"]["line3"]
            store.append(address)
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["subdivision"])
            store.append(store_data["address"]["postalCode"])
            if len(store[-1]) == 10:
                store[-1] = store[-1][:5] + "-" + store[-1][6:]
            print(store[-1])
            store.append(store_data["address"]["country"])
            store.append(store_data["id"])
            store.append(store_data["phone"])
            store.append("<MISSING>")
            store.append(store_data["lat"])
            store.append(store_data["lon"])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
