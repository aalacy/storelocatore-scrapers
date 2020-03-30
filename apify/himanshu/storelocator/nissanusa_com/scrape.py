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
    base_url = "https://www.nissanusa.com"
    r = session.get("https://www.nissanusa.com/dealer-locator.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for script in soup.find_all('script'):
        if "apigee" in script.text:
            api_key = script.text.split("apigee")[1].split('apiKey":')[1].split(",")[0].replace('"',"")[1:]
            clientKey = script.text.split("apigee")[1].split('clientKey":')[1].split(",")[0].replace('"',"")[1:]
    api_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "clientKey":clientKey,
        "apiKey":api_key
    }
    r = session.get("https://us.nissan-api.net/v2/dealers?size=10000000&serviceFilterType=AND&include=openingHours",headers=api_headers)
    return_main_object = []
    location_list = r.json()["dealers"]
    for i in range(len(location_list)):
            store_data = location_list[i]
            store = []
            store.append("https://www.nissanusa.com")
            store.append(store_data["name"])
            store.append(store_data["address"]["addressLine1"] + " " + store_data["address"]["addressLine2"])
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["stateCode"])
            store.append(store_data["address"]["postalCode"])
            store.append("US")
            store.append("<MISSING>")
            store.append(store_data["contact"]["phone"] if store_data["contact"]["phone"]  != "" else "<MISSING>")
            store.append("nissan")
            store.append(store_data["geolocation"]["latitude"])
            store.append(store_data["geolocation"]["longitude"])
            store.append(store_data["openingHours"]["openingHoursText"].replace("\n"," ") if store_data["openingHours"]["openingHoursText"]  != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
