import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
    }

    addresses = []
    base_url = "http://www.charlotterusse.com"

    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = ''
    url = "https://charlotterusse.com/apps/api/v1/stores"

    
    json_data = session.get(url, headers=headers).json()
    # soup = BeautifulSoup(r.text, "lxml")

    # print("json_data === "+ str(json_data))
    for location in json_data["stores"]:

        # print("location === " + str(location))
        street_address = location["address"]["line1"] +" "+ location["address"]["line2"]+" "+ location["address"]["line3"]
        location_name = location["address"]["name"]
        city = location["address"]["city"]
        state = location["address"]["state_code"]
        country_code = location["address"]["country_code"]
        zipp = location["address"]["zip"]
        latitude = str(location["address"]["latitude"])
        longitude = str(location["address"]["longitude"])
        store_number = str(location["store_code"])
        phone = location["phone"]
        location_type = location['brand']
    
        hours_of_operation = ""
        for hours_day in location["open_hours"]:
            if "closed" in hours_day:
                hours_of_operation += hours_day["day"] +" "+hours_day["closed"] +" "
            else:
                hours_of_operation += hours_day["day"] +" "+hours_day["open_time"] +" - "+hours_day["close_time"] +" "

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses and "coming soon" not in location_name.lower():
            addresses.append(str(store[1]) + str(store[2]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
