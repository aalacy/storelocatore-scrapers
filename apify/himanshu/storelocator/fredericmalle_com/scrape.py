import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "raw_address"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    addresses = []

    base_url = "https://www.fredericmalle.com"
    r = requests.get("https://www.fredericmalle.com/about#stores", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<INACCESSIBLE>"
    city = "<INACCESSIBLE>"
    state = "<INACCESSIBLE>"
    zipp = "<INACCESSIBLE>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "fredericmalle"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # print("data ====== "+str(soup))
    for script in soup.find_all("div", {"class": "stores__location-info"}):
        address_list = list(script.stripped_strings)

        for i in range(len(address_list)):
            address_list[i] = re.sub('[^A-Za-z0-9 ]+', '', address_list[i])

        location_name = address_list[0]

        hours_of_operation = "<MISSING>"

        if "Get Directions" in address_list:
            hours_of_operation = " ".join(address_list[(address_list.index("Get Directions")) + 1:])
            phone = address_list[:(address_list.index("Get Directions"))][-1]
            raw_address = ",".join(address_list[:(address_list.index("Get Directions"))][1:-1])
        else:
            phone = address_list[-1]
            raw_address = ",".join(address_list[1:-1])

        if hours_of_operation.strip() == "":
            hours_of_operation = "<MISSING>"

        if "TEL" not in phone:
            phone = "<MISSING>"
        else:
            phone = phone.replace("TEL", "").strip()

        # print("hours_of_operation === " + str(hours_of_operation))

        country_code = "US"

        if script.find('a') is not None:
            map_location = script.find('a')['href']

            if len(map_location.split("&sll=")) > 1:
                latitude = map_location.split("&sll=")[1].split("&")[0].split(",")[0]
                longitude = map_location.split("&sll=")[1].split("&")[0].split(",")[1]
            elif len(map_location.split("/@")) > 1:
                latitude = map_location.split("/@")[1].split(",")[0]
                longitude = map_location.split("/@")[1].split(",")[1]
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            # print("map URL ===== " + str(script.find('a')['href']))
            # print("latitude ===== " + str(latitude))
            # print("longitude ===== " + str(longitude))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, raw_address]

        if str(store[-1]) + str(store[-3]) not in addresses:
            addresses.append(str(store[-1]) + str(store[-3]))

            store = [x if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
