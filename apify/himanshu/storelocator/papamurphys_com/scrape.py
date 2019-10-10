import csv
import time

import requests
from bs4 import BeautifulSoup
import re
import json



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    }

    addresses = []
    base_url = "https://www.papamurphys.com"

    r_state = requests.get("https://order.papamurphys.com/locations", headers=headers)
    soup_state = BeautifulSoup(r_state.text, "lxml")

    for state_script in soup_state.find("ul", {"id": "ParticipatingStates"}).find_all("a"):
        state_url = "https://order.papamurphys.com" + state_script["href"]

        # print("state_url == " + state_url)

        r_all_locations = requests.get(state_url, headers=headers)
        soup_all_locations = BeautifulSoup(r_all_locations.text, "lxml")

        for location_script in soup_all_locations.find_all("li", {"class": "vcard"}):

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
            page_url = ""

            location_name = location_script.find("span", {"class": "fn org"}).text.strip()
            if location_script.find("h2").find("a"):
                page_url = location_script.find("h2").find("a")["href"]

            street_address = location_script.find("span", {"class": "street-address"}).text.strip()
            city = location_script.find("span", {"class": "locality"}).text.strip()
            state = location_script.find("span", {"class": "region"}).text.strip()
            phone = location_script.find("div", {"class": "location-tel-number"}).text.strip()
            latitude = str(location_script.find("span", {"class": "latitude"}).find("span")["title"])
            longitude = str(location_script.find("span", {"class": "longitude"}).find("span")["title"])

            # print("page_url == " + str(page_url))
            if page_url:
                r_location = requests.get(page_url, headers=headers)
                soup_location = BeautifulSoup(r_location.text, "lxml")
                zipp = soup_location.find("span", {"class": "postal-code"}).text.strip()
                if soup_location.find("dl", {"class": "available-hours"}):
                    hours_of_operation = " ".join(list(soup_location.find("dl", {"class": "available-hours"}).stripped_strings))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses:
                addresses.append(str(store[1]) + str(store[2]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
