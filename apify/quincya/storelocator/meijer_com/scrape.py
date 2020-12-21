import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgselenium import SgChrome

log = SgLogSetup().get_logger("meijer.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    driver = SgChrome().chrome()

    data = []
    locator_domain = "meijer.com"

    for page_num in range(50):
        base_link = (
            "https://www.meijer.com/shop/en/store-finder/search?q=60010&page=%s&radius=4500"
            % page_num
        )
        log.info(base_link)
        driver.get(base_link)

        base = BeautifulSoup(driver.page_source, "lxml")
        stores = json.loads(base.text)["data"]

        if len(stores) == 0:
            break

        for store in stores:
            location_name = store["displayName"]
            street_address = (store["line1"] + " " + store["line2"]).strip()
            city = store["town"]
            state = store["state"]
            zip_code = store["postalCode"]
            country_code = "US"
            store_number = store["name"]
            location_type = "<MISSING>"
            phone = store["phone"]
            hours_of_operation = "<INACCESSIBLE>"
            latitude = store["latitude"]
            longitude = store["longitude"]
            link = "https://www.meijer.com/shop/en/store/" + store_number

            # Store data
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
