# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "winerack.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.winerack.com/assets/js/winerack-locations-lookup.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)

    for store in stores:
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["id"]
        street_address = store["fullAddress"].split(",")[0].strip()
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()

        city = store["city"]
        state = store["province"]
        zip = store["postalCode"]

        country_code = "CA"

        store_number = ""
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip().replace(")", "").strip()

        phone = "<INACCESSIBLE>"
        hours_of_operation = "<INACCESSIBLE>"
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]

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
