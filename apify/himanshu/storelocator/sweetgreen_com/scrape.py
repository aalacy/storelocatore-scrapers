import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addresses = []
    base_url = "https://order.sweetgreen.com/"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""

    r = requests.get(
        "https://order.sweetgreen.com/api/restaurants?page=1&per=1000", headers=headers).json()
    for loc in r["restaurants"]:
        location_name = loc["name"]
        store_number = loc["id"]
        street_address = loc["address"]
        city = loc["city"]
        state = loc["state"]
        zipp = loc["zip_code"]
        phone = loc["phone"]
        hours_of_operation = loc["store_hours"]
        latitude = loc["latitude"]
        longitude = loc["longitude"]
        a = location_name.lower().strip().replace("sg outpost at","").replace("sg outpost at ","").lstrip().replace(" ","-").replace("---","-").replace("--","-").replace(".","").replace(",","").replace("–-","").replace("&-","").replace("+-","").replace("(","").replace(")","").replace("'","-").replace("/","")
        page_url = "https://order.sweetgreen.com/"+str(a)+"/menu"
        if "11111111111" == phone or "11000000000" == phone:
            phone = "<MISSING>"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" or x == None else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        if store_number in addresses:
            continue
        addresses.append(store_number)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
