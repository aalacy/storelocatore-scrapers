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
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S %p")
    addresses = []
    data = '{"timestamp":"'+str(timestamp)+'","radius":804679,"restaurantStatuses":["OPEN"],"conceptIds":["CMG"],"orderBy":"distance","orderByDescending":"false","pageSize":10000,"pageIndex":0,"embeds":{"addressTypes":["MAIN"],"publicPhoneTypes":["MAIN PHONE"],"realHours":"true","normalHours":"true","directions":"true","catering":"true","onlineOrdering":"true"}}' 
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'b4d9f36380184a3788857063bce25d6a',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Cookie': 'f5avrbbbbbbbbbbbbbbbb=BICEEDMJHEEIPPKKLCHLEGPPJAPGBHCOBFCJIPDFFNNBEMEKBDEBPPGJKEFAIGGMDGGJGCENDJHDIAAKMGKMDKMMJLLADGLEBPBCKGAIDPIHLMNJCEMNGJIMBHJJOPOK; ADRUM_BTa=R:0|g:7ffa7868-95e7-48bf-99f2-759a08b51a76|n:chipotle-prod_20db0ee1-fc55-47c0-9912-7a6fbdf65d4d; ADRUM_BT1=R:0|i:2259539; TS01811d4a=0106a0d561b565a08954c97da32677a5cfc4f0b0ec21634ffecfbe395a950fd46f9737925e00c4c5830eed8c4c6d1d0c86bf804798919d24b2cee76337825469e9122e1eefbad495826a0cbfb78ffed5d14df3fd61'
    }
    base_url = "https://chipotle.com"
    r = session.post("https://services.chipotle.com/restaurant/api/v2.1/search",data=data, headers=headers)
    data = r.json()["data"]
    for i in range(len(data)):
        store_data = data[i]
        if "Cultivate Center" in store_data['restaurantName']:
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
        try:
            phone = store_data["publicPhones"][0]["phoneNumber"]
        except:
            phone = "<MISSING>"
        store.append(phone)
        store.append(store_data["restaurantLocationType"])
        try:
            store.append(store_data['addresses'][0]["latitude"])
            store.append(store_data['addresses'][0]["longitude"])
        except:
            store.append("<MISSING>")
            store.append("<MISSING>")
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
