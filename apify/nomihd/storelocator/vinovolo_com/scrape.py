# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape import sgpostal as parser

website = "vinovolo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    api1_url = "https://www.vinovolo.com/api/locations/cities?_=1617887060143"
    api2_url = "https://www.vinovolo.com/api/locations/stores?_=1617887060144"
    api1_res = session.get(api1_url, headers=headers)
    api2_res = session.get(api2_url, headers=headers)

    cities_list = json.loads(api1_res.text)
    stores_list = json.loads(api2_res.text)

    addresses = dict()
    for location in cities_list:
        key = location["title"].strip()  # Key will be the title
        addresses[key] = location["address"].strip()

    for store in stores_list:

        page_url = "<MISSING>"

        locator_domain = website
        location_name = store["name"].strip()

        # use title to get the address from dictionary.
        title = store["title"].strip()
        raw_address = addresses[title]

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country = formatted_addr.country
        if country == "Canada":
            country_code = "CA"
        else:
            country_code = "US"

        store_number = "<MISSING>"
        phone = store["phone"].strip()

        store_hours = store["hours"]
        if store_hours == "Temporarily Closed":

            location_type = "Temporarily Closed"
            hours_of_operation = "<MISSING>"

        else:
            location_type = "<MISSING>"
            hours_of_operation = store_hours

        latitude = store["latitude"]
        longitude = store["longitude"]
        if "-" in longitude:
            longitude = "<MISSING>"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
