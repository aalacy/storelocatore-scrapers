# coding=UTF-8

import csv
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
session = SgRequests()
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',

    }

    base_url = "https://www.urgentteam.com/brand/sherwood-urgent-care/"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "Sherwood Urgent Care"
    latitude = ""
    longitude = ""
    hours = ""
    page_url = ""
    r = session.get("https://www.urgentteam.com/locations/?address=&lat=&lng=&brand=sherwood-urgent-care", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for url in soup.find_all("a",{"class":"m-location__cta"}):
        page_url = url['href']
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        data = json.loads(soup1.find(lambda tag:(tag.name == "script") and "latitude" in tag.text).text)
        location_name = data['name']
        street_address = data['address']['streetAddress']
        city = data['address']['addressLocality']
        state = data['address']['addressRegion']
        zipp = data['address']['postalCode']
        phone = data['telephone']
        latitude = data['geo']['latitude']
        longitude = data['geo']['longitude']
        hours = " ".join(list(soup1.find("div",{"class":"m-location-panel__hours m-location-hours"}).stripped_strings))
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, str(latitude), str(longitude), hours,page_url]

        # if str(store[2]) + str(store[-3]) not in addresses:
        #     addresses.append(str(store[2]) + str(store[-3]))

        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
