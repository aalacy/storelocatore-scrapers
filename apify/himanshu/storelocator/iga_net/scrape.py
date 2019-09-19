import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    zips = sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # it will used in store data.
    locator_domain = "https://www.iga.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "iga"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    r = requests.get(
        "https://www.iga.net/api/en/Store/get?Latitude=45.489599&Longitude=-73.585324&Skip=0&Max=324", headers=headers);

    json_data = r.json()
    # print("--json==" + str(json_data))
    # print("~~~~~~~~~~~~~~~~~`")

    for x in json_data['Data']:
        locator_domain = "https://www.iga.com/"
        location_name = x['Name']
        hours_of_operation = x['OpeningHours']
        street_address = x['AddressMain']['Line']
        city = x['AddressMain']['City']
        state = x['AddressMain']['Province']
        zipp = x['AddressMain']['PostalCode']
        phone = x['PhoneNumberHome']['Number']
        latitude = x['Coordinates']['Latitude']
        longitude = x['Coordinates']['Longitude']
        raw_address = x['RawName']
        store_number = x['Number']
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]
        store = ["<MISSING>" if x == "" else x for x in store]
        print("data = " + str(store))
        print(
            '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
