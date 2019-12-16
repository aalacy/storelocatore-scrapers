import csv
import requests
from bs4 import BeautifulSoup
import re
import io
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
    return_main_object = []
    base_url = "https://www.chilis.com"
    locator_domain = base_url
    location_type = "<MISSING>"
    country_code = "US"
    r = requests.get(
        "https://www.chilis.com/locations/us/all", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for values in soup.findAll('a', {'class', 'city-link'}):
        # try:
        detail_page_url = "https://www.chilis.com" + values.get('href')
        # print(detail_page_url)
        try:
            detail_url = requests.get(detail_page_url, headers=headers)
        except:
            pass

        detail_soup = BeautifulSoup(detail_url.text, "lxml")
        script = detail_soup.find(lambda tag: (
            tag.name == "script") and "Chilis.LocationData" in tag.text)
        script_text = script.text.split("locationsList:")[
            1].split("]")[0] + "]"
        # print(script_text)
        json_data = json.loads(script_text)
        for loc in json_data:
            store_number = loc["restaurantId"]
            location_name = loc["name"]
            street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zipp = loc["zipCode"]
            phone = loc["phone"]
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            page_url = base_url + loc["detailsUrl"]
            # print(page_url)
            r_loc = requests.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, 'lxml')
            hours = soup_loc.find(
                "div", class_="location-hours-container")
            if hours == None:
                hours_of_operation = "MISSING"
            else:
                hours_of_operation = " ".join(list(soup_loc.find(
                    "div", class_="location-hours-container").stripped_strings)).strip().replace("Hours", "").strip()
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(
                hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url)
            attr = store[1] + "" + store[2] + "" + \
                store[3] + "" + store[4] + "" + store[5]

            if attr in addresses:
                continue
            addresses.append(attr)
            return_main_object.append(store)
            print("data = " + str(store))
            print(
                '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
