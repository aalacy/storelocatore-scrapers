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
    base_url = "https://www.ctshirts.com"
    r = session.get("https://liveapi.yext.com/v2/accounts/me/locations?api_key=74daf99313eb1189e461442a605c448b&v=20071001&limit=50")
    data = r.json()["response"]["locations"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.ctshirts.com")
        store.append(store_data['locationName'])
        store.append(store_data["address"] + store_data["address2"] if "address2" in store_data else store_data["address"])
        store.append(store_data['city'])
        store.append(store_data['state'] if "state" in store_data else "<MISSING>")
        store.append(store_data['zip'])
        store.append(store_data["countryCode"])
        if store[-1] not in ("US","CA"):
            continue
        store.append(store_data["id"])
        store.append(store_data["phone"])
        store.append("charles tyrwhitt")
        store.append(store_data['yextDisplayLat'])
        store.append(store_data['yextDisplayLng'])
        days = {"2": "Monday","3":"Tuesday","4":"Wednesday","5":"Thursday","6":"Friday","7":"Saturday","1":"Sunday"}
        store_hours = store_data["hours"].split(",")
        if store_hours == [""]:
            store_hours = ""
        hours = ""
        for k in range(len(store_hours)):
            hours = hours + " " + days[store_hours[k][0]] + " from " + ":".join(store_hours[k].split(":")[1:3]) + " to " + ":".join(store_hours[k].split(":")[3:])
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
