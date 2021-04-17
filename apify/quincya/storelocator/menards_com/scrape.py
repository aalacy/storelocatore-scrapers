import csv
import json

from bs4 import BeautifulSoup

from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://www.menards.com/main/storeLocator.html"

    driver = SgChrome().driver()
    driver.get(base_link)

    base = BeautifulSoup(driver.page_source, "lxml")

    data = []

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "initialStores" in str(script):
            script = str(script)
            break

    locator_domain = "menards.com"

    js = script.split("initialStores =")[1].split(";\n")[0].strip()
    stores = json.loads(js)

    for store in stores:
        location_name = store["name"]
        street_address = store["street"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = store["number"]
        phone = "<INACCESSIBLE>"
        hours_of_operation = "<INACCESSIBLE>"
        latitude = store["latitude"]
        longitude = store["longitude"]

        location_type = ""
        loc_types = store["services"]
        for loc_type in loc_types:
            location_type = location_type + ", " + loc_type["displayName"]
        location_type = location_type[1:].strip()

        link = "https://www.menards.com/main/storeDetails.html?store=" + str(
            store_number
        )
        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
