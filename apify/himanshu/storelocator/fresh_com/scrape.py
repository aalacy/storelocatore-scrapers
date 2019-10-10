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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    addresses = []
    base_url = "https://www.fresh.com"

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

    r = requests.get("https://www.fresh.com/us/customer-service/USShops.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # print("souip ==== "+ r.text)

    for script in soup.find_all("p", {"class": "subheader1 privacy-info-question"}):
        script_parent = script.parent
        script_location = script_parent.findNext("div").find("p")

        full_address = list(script_location.stripped_strings)
        location_name = script_parent.find("a").text

        street_address = full_address[0]

        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address[1]))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address[1]))
        state_list = re.findall(r' ([A-Z]{2}) ', full_address[1])

        phone = ""
        state = ""
        zipp = ""

        if phone_list:
            phone = phone_list[0]

        if ca_zip_list:
            zipp = ca_zip_list[0]
            country_code = "CA"

        if us_zip_list:
            zipp = us_zip_list[0]
            country_code = "US"

        if state_list:
            state = state_list[0]

        city = full_address[1].replace(zipp, "").replace(state, "").replace(",", "")

        page_url = script.find("a")["href"]

        r_location = requests.get(page_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        hours_of_operation = " ".join(list(soup_location.find("div",{"class":"ywidget biz-hours"}).stripped_strings)[:-1])
        # print("soup_location ==== "+ soup_location.text)
        latitude = str(r_location.text.split("latitude")[1].split(",")[0].split(" ")[-1].strip())
        longitude = str(r_location.text.split("longitude")[1].split("}")[0].split(" ")[-1].strip())
        # print("latitude == "+ str(latitude))
        # print("longitude == "+ str(longitude))
        # print("location == " + str(full_address))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses:
            addresses.append(str(store[1]) + str(store[2]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
