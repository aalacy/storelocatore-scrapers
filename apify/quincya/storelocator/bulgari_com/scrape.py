import csv
import json

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests


logger = SgLogSetup().get_logger("bulgari_com")


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

    base_links = [
        "https://www.bulgari.com/en-us/storelocator/united+states",
        "https://www.bulgari.com/en-us/storelocator/canada",
    ]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []

    for base_link in base_links:
        logger.info(base_link)
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "bulgari.com"

        js = base.find(class_="map-canvas")["data-locations"]
        stores = json.loads(js)

        for store in stores:

            location_name = store["name"]
            street_address = (
                store["storeAddress"]
                .replace("Hills, Ca", "Hills")
                .replace("Gables, Fl", "Gables")
                .replace("Las Vegas, NV", "")
            )
            city = store["storeCity"].replace("+", " ").title()

            if city in street_address and "las vegas" not in street_address.lower():
                street_address = (
                    street_address[: street_address.rfind(city)]
                    .strip()
                    .replace("  ", " ")
                )

            if street_address[-1:] == ",":
                street_address = street_address[:-1].strip()

            country_code = store["storeCountry"].replace("+", " ").title()
            store_number = store["storeId"]
            location_type = "<MISSING>"
            try:
                phone = store["storePhone"].strip()
            except:
                phone = "<MISSING>"
            latitude = store["latitude"]
            longitude = store["longitude"]
            link = (
                "https://www.bulgari.com/en-us/storelocator/"
                + store["storeCountry"]
                + "/"
                + store["storeCity"]
                + "/"
                + store["storeNameUrl"]
                + "-"
                + store_number
            )
            logger.info(link)

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            raw_address = (
                base.find(class_="storelocator-bread-subtitle").text.strip().split("\n")
            )
            state = raw_address[-2].strip()
            if not state:
                raw_state = (
                    base.find(class_="storelocator-bread-subtitle")
                    .text.replace("\n", " ")
                    .strip()
                )
                state = raw_state[
                    raw_state.rfind(",") + 1 : raw_state.rfind(" ")
                ].strip()

            zip_code = raw_address[-1].strip()

            try:
                hours_of_operation = " ".join(
                    list(base.find(class_="store-hours clearfix").stripped_strings)
                )
            except:
                hours_of_operation = "<MISSING>"

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

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
