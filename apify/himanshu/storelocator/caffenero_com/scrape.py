import csv
#import sys
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "raw_address", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://caffenero.com/"

    addresses = []
    result_coords = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "Uk"
    store_number = ""
    phone = ""
    location_type = "<MISSING>"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = ""
    r = requests.get(
        "https://caffenero.com/uk/stores/?country-code=gb&place=W1A&search-region=W1A")
    soup = BeautifulSoup(r.text, "lxml")
    script = soup.find(lambda tag: (
        tag.name == 'script') and "storesData" in tag.text).text.split("storesData =")[1].split(';')[0].strip()
    json_data = json.loads(script)
    for loc in json_data["stores"]:
        if "gb" in loc["country_code"]:
            # country_code = loc["country_code"]
            store_number = loc["store_id"]
            location_name = loc["name"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            raw_address = " ".join(loc["address"].split(',')[:-1])
            street_address = "<INACCESSIBLE>"
            city = "<INACCESSIBLE>"
            state = "<INACCESSIBLE>"
            zipp = loc["address"].split(',')[-1].strip()
            page_url = "https://caffenero.com" + loc["permalink"]

            r_loc = requests.get(page_url)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            try:
                phone = soup_loc.find(
                    "img", {"alt": "phone"}).find_next("td").text.strip()
            except:
                phone = "<MISSING>"
            try:
                hours_of_operation = " ".join(
                    list(soup_loc.find("div", class_="timings-info").stripped_strings)).replace("Opening Hours", "").strip()
            except:
                hours_of_operation = "<MISSING>"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, raw_address, page_url]

            if str(store[7]) not in addresses:
                addresses.append(str(store[7]))
                store = [x if x else "<MISSING>" for x in store]
                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
