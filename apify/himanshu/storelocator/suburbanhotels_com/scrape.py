import csv
# from sgrequests import SgRequests
import requests
from bs4 import BeautifulSoup
import re
import json
import datetime
import sys
import os

tomorrow = datetime.date.today() + datetime.timedelta(days=1)
next_day = datetime.date.today() + datetime.timedelta(days=2)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


# session = SgRequests()


def fetch_data():
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    # }
    base_url = "https://www.suburbanhotels.com"

    addresses = []
    result_coords = []
    locator_domain = base_url
    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"
    url = "https://www.choicehotels.com/webapi/location/hotels"

    querystring = {"adults": "1", "checkInDate": "" + str(tomorrow) + "", "checkOutDate": "" + str(next_day) + "", "hotelSortOrder": "RELEVANCE", "include": "amenity_groups%2C%20amenity_totals%2C%20rating%2C%20relative_media", "minors": "0", "optimizeResponse": "image_url", "placeName": "suburban%20collection%20showplace",
                   "platformType": "DESKTOP", "preferredLocaleCode": "en-gb", "ratePlanCode": "RACK", "ratePlans": "RACK%2CPREPD%2CPROMO%2CFENCD", "rateType": "LOW_ALL", "rooms": "1", "searchRadius": "100", "siteName": "uk", "siteOpRelevanceSortMethod": "ALGORITHM_B", "stateCountry": "michigan"}

    headers = {
        'Content-type': "application/json, text/plain, */*",
        'User-Agent': "PostmanRuntime/7.20.1",
        'Accept': "*/*"

    }

    response = requests.request(
        "POST", url, headers=headers, params=querystring).json()

    location_type = response["places"][0]["name"]
    for loc in response["hotels"]:
        store_number = loc["id"]
        location_name = loc["name"]
        street_address = loc["address"]["line1"]
        city = loc["address"]["city"]
        state = loc["address"]["subdivision"]
        # print(state)
        zipp = loc["address"]["postalCode"]
        country_code = loc["address"]["country"]
        phone = loc["phone"]
        latitude = loc["lat"]
        longitude = loc["lon"]
        page_url = "<MISSING>"
        store = [locator_domain, location_name.encode('ascii', 'ignore').decode('ascii').strip(), street_address.encode('ascii', 'ignore').decode('ascii').strip(), city.encode('ascii', 'ignore').decode('ascii').strip(), state.encode('ascii', 'ignore').decode('ascii').strip(), zipp.encode('ascii', 'ignore').decode('ascii').strip(), country_code,
                 store_number, phone.encode('ascii', 'ignore').decode('ascii').strip(), location_type, latitude, longitude, hours_of_operation.replace("hours", "").encode('ascii', 'ignore').decode('ascii').strip(), page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))
            store = [x if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
