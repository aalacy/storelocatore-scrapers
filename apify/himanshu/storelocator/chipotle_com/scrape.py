import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = '{"timestamp":"2019-07-20T11:32:46.698Z","radius":804679,"restaurantStatuses":["OPEN"],"conceptIds":["CMG"],"orderBy":"distance","orderByDescending":false,"pageSize":10000,"pageIndex":0,"embeds":{"addressTypes":["MAIN"],"publicPhoneTypes":["MAIN PHONE"],"realHours":true,"normalHours":true,"directions":true,"catering":true,"onlineOrdering":true}}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://chipotle.com"
    r = requests.post(base_url + "/api/v2.1/search",data=data,headers=headers)
    data = r.json()["data"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://chipotle.com")
        store.append(store_data['restaurantName'])
        if "addressLine1" not in store_data["addresses"][0]:
            continue
        store.append(store_data["addresses"][0]["addressLine1"] + store_data["addresses"][0]["addressLine2"] if "addressLine2" in store_data["addresses"][0] else store_data["addresses"][0]["addressLine1"])
        store.append(store_data['addresses'][0]["locality"])
        store.append(store_data['addresses'][0]["administrativeArea"] if "administrativeArea" in store_data['addresses'][0] else "<MISSING>")
        store.append(store_data['addresses'][0]["postalCode"])
        store.append(store_data['country']["countryCode"])
        store.append(store_data["restaurantNumber"])
        store.append(store_data["publicPhones"][0]["phoneNumber"])
        store.append("chipotle")
        store.append(store_data['addresses'][0]["latitude"])
        store.append(store_data['addresses'][0]["longitude"])
        store_hours = store_data["normalHours"]
        hours = ""
        for k in range(len(store_hours)):
            hours = hours + " " + store_hours[k]["dayOfWeek"] + " from " + store_hozzurs[k]["openTime"] + " to " + store_hours[k]["closeTime"]
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
