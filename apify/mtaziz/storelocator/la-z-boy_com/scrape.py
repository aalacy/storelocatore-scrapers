from sgrequests import SgRequests
from sglogging import SgLogSetup
import csv
import json
from lxml import html
from time import sleep
from random import randint


MISSING = "<MISSING>"
logger = SgLogSetup().get_logger("la-z-boy_com")
session = SgRequests()
locator_domain_url = "https://www.la-z-boy.com"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def get_hoo(url_hoo):
    try:
        r_hours = session.get(url_hoo, headers=headers)
        sleep(randint(1, 3))
        r_hoo_data = html.fromstring(r_hours.text, "lxml")
        xpath_hoo = '//script[@type="application/ld+json"]/text()'
        hoo_raw_data = r_hoo_data.xpath(xpath_hoo)
        logger.info(f"HOO Raw Data: {hoo_raw_data}\n")
        hoo_raw_data = "".join(hoo_raw_data)
        if hoo_raw_data:
            hoo_data_json = json.loads(hoo_raw_data)
            hoo_data_json = hoo_data_json["openingHours"]
            if hoo_data_json:
                return hoo_data_json
            else:
                return MISSING
        else:
            return MISSING
    except Exception:
        return MISSING


def fetch_data():
    url_all_stores = "https://www.la-z-boy.com/storeLocator/json/storeResultByCoordinates.jsp?latitude=40.84924816795747&longitude=-73.821&distance=10076143.5&sortOption=1"
    data_main = session.get(url_all_stores, headers=headers).json()
    items = []
    total = 0
    country_code_ca = "CA"
    country_code_us = "US"

    for idx, d in enumerate(data_main[0]["map"]):
        country_code = d["country"]
        if country_code == country_code_ca or country_code == country_code_us:
            locator_domain = locator_domain_url
            location_name = d["storename"] if d["storename"] else MISSING
            street_address = d["address1"] if d["address1"] else MISSING
            city = d["city"]
            city = city if city else MISSING
            state = d["state"] if d["state"] else MISSING
            zip = d["zip"] if d["zip"] else MISSING
            country_code = d["country"] if d["country"] else MISSING
            store_number = d["storeID"] if d["storeID"] else MISSING
            phone = d["phone"] if d["phone"] else MISSING
            location_type = MISSING
            latitude = d["lat"] if d["lat"] else MISSING
            longitude = d["longi"] if d["longi"] else MISSING
            url_store = d["website"]
            hours_of_operation = MISSING
            if url_store:
                if "http" in url_store:
                    page_url = url_store.lower()
                else:
                    page_url = f"{locator_domain_url}{url_store.lower()}"
            else:
                page_url = MISSING
            hours_of_operation = MISSING
            logger.info(f"Scraping HOO Row Number: {idx}")
            if not page_url == MISSING:
                logger.info(f"Scraping HOO Data from: {page_url}")
                hours_of_operation = get_hoo(page_url)

            row = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
                page_url,
            ]
            items.append(row)
            total += 1
    logger.info(f"Total Store Count: {total}")
    return items


def scrape():
    logger.info("Scraping Started....")
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
