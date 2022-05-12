# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "buffalowildwings.ph"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(verify_ssl=False)
headers = {
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.buffalowildwings.ph/branch"
    search_res = session.get(search_url, headers=headers)
    stores = json.loads(
        search_res.text.split("let branches = ")[1].strip().split(";")[0].strip()
    )
    for store in stores:
        page_url = search_url
        locator_domain = website

        location_name = store["name"]

        raw_address = store["location"]
        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        if not city:
            city = raw_address.split(",")[-1].strip()
            street_address = raw_address.split(",")[0].strip()

        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "PH"

        store_number = store["id"]

        location_type = "<MISSING>"
        phone = store["contact_number"]
        if phone:
            phone = phone.split("|")[0].strip()

        hours_of_operation = store["description"]
        if hours_of_operation:
            hours_of_operation = hours_of_operation.replace("  ", "; ").strip()
        latitude, longitude = store["latitude"], store["longitude"]

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
