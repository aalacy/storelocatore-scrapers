import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    addresses = []
    base_url = "https://www.educationaloutfitters.com"
    r = requests.get("http://www.educationaloutfitters.com/states", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "educationaloutfitters"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for script in soup.find_all("div", {"class": "p-name"}):
        location_name = script.text

        print(location_name + " === " + str(script.find("a")["href"]))
        location_url = script.find("a")["href"]
        r_location = requests.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "html.parser")

        full_detail = list(soup_location.find("div", {"class": "ProductDetailsGrid ProductAddToCart"}).stripped_strings)

        full_address = ",".join(full_detail[full_detail.index("\uf041") + 1:full_detail.index("\uf0e0")]).split(",")

        street_address = ", ".join(full_address[:-2])
        if street_address != "":
            if full_address[-2] == "":
                city = location_name
            else:
                city = full_address[-2]
        else:
            street_address = full_address[0]
            city = location_name

        if len(full_address[-1].strip().split(" ")) > 2:
            state = "<MISSING>"
            zipp = "<MISSING>"
        else:
            if len(full_address[-1].strip().split(" ")) > 1:
                state = full_address[-1].strip().split(" ")[0]
                zipp = full_address[-1].strip().split(" ")[-1]
            else:
                if full_address[-1].strip().isdigit():
                    zipp = full_address[-1].strip()
                    state = "<MISSING>"
                else:
                    state = full_address[-1].strip()
                    zipp = "<MISSING>"

        phone = full_detail[full_detail.index("\uf095")+1]

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
