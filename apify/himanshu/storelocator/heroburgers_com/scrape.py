# coding=UTF-8

import csv
import re

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://heroburgers.com/"
    location_url = "https://onlineordering.zone1.mealsyservices.com/api/v1/Companies/POSHeroCertifiedBurgers/Businesses"
    r = session.get(location_url, headers=headers)
    json_data = r.json()

    for val in json_data["Businesses"]:
        location_name = val["Foodprovider"]["Name"]
        addr = val["Foodprovider"]["Address"].split(",")
        if len(addr) == 4:
            street_address = ",".join(addr[:2]).strip()
            city = addr[2].strip()
            state = addr[-1].strip()
            country_code = "CA"
        elif len(addr) == 3:
            street_address = addr[0].strip()
            city = addr[1].strip()
            state = addr[2].strip()
            country_code = "CA"
        else:
            city = "New York"
            street_address = addr[0].replace(city, "").strip()
            state = addr[1].strip()
            country_code = "US"

        digit = re.search(r"\d", street_address).start(0)
        if digit != 0:
            street_address = street_address[digit:]

        zipp = val["Foodprovider"]["PostalCode"]
        store_number = val["Foodprovider"]["Id"]
        phone = val["Foodprovider"]["Tell"]
        latitude = val["Foodprovider"]["Longitude"]
        longitude = val["Foodprovider"]["Latitude"]

        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
