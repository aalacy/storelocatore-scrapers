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

    base_url = "http://www.multi-specialty.com"
    addresses = []

    r = requests.get("http://www.multi-specialty.com/all_locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # print("soup === "+ str(soup.text))
    for locations in soup.find("div", {"class": "content_box"}).find_all("div")[1:-1]:

        locations_list = str(locations).split("<strong")

        for loc in locations_list:

            tags_address = BeautifulSoup("<strong" + loc, "lxml")
            list_address = list(tags_address.stripped_strings)

            if len(list_address) < 3:
                continue

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

            # do your logic here.
            # print("loc ==~~~~~~~~~~~~~~~~~= " + str(list_address))

            location_name = list_address[0]

            raw_address = str(list_address).replace(r"\t", " ")
            # print("raw_address == " + raw_address)
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), raw_address)
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', raw_address)
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), raw_address)
            state_list = re.findall(r' ([A-Z]{2}) ', raw_address)

            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            if state_list:
                state = state_list[-1]

            zipp_index = [i for i, s in enumerate(list_address) if zipp in s]
            street_address = " ".join(list_address[1:zipp_index[0]])
            street_address = street_address.replace("\t", " ")
            city = list_address[zipp_index[0]].split(",")[0]
            phone = phone_list[0]

            # print("state ===  "+ str(state))
            geo_url = tags_address.find("a",{"href":re.compile(".google.com")})

            if geo_url:
                geo_url = geo_url["href"]

                if "sll=" in geo_url:
                    latitude = geo_url.split("sll=")[1].split("&")[0].split(",")[0]
                    longitude = geo_url.split("sll=")[1].split("&")[0].split(",")[1]
                if "/@" in geo_url:
                    latitude = geo_url.split("/@")[1].split(",")[0]
                    longitude = geo_url.split("/@")[1].split(",")[1]

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2] +" "+store[1]) not in addresses and country_code:
                addresses.append(str(store[2] +" "+store[1]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
