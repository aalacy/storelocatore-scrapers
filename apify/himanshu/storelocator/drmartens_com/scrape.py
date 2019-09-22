import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.drmartens.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "drmartens"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for zip_code in zips:
        # print("zips === " + str(zip_code))

        page_no = 0
        isFinish = False
        while isFinish is not True:
            # zip_code = 11576

            location_url = "https://www.drmartens.com/us/en/store-finder?q=" + str(zip_code) + "&page=" + str(page_no)

            # print("location_url === " + location_url)
            r = requests.get(location_url, headers=headers)

            try:
                json_data = r.json()
            except:
                break

            for address_list in json_data['data']:

                # print("address_list === " + str(address_list))
                location_name = address_list['displayName']
                latitude = address_list['latitude']
                longitude = address_list['longitude']
                phone = address_list['phone'].replace("Phone", "").replace(":", "")
                street_address = address_list['line1'] + " " + address_list['line2']

                if len(address_list['town'].split(',')) > 1:
                    city = address_list['town'].split(',')[0]
                    state = address_list['town'].split(',')[1]
                elif len(address_list['town'].split(' ')) > 1:
                    city = address_list['town'].split(' ')[0]
                    state = address_list['town'].split(' ')[1]
                else:
                    state = address_list['town']
                    city = ""

                zipp = address_list['postalCode']

                if zipp.isdigit():
                    country_code = "US"
                else:
                    country_code = "CA"

                if 'openings' in address_list:
                    hours_of_operation = str(address_list['openings']).replace('{', "").replace('}', "")
                else:
                    hours_of_operation = ""

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                if store[2] + store[-3] not in addresses:
                    addresses.append(store[2] + store[-3])

                    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store

            page_no += 1


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
