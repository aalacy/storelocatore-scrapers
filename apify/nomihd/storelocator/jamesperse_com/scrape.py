# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jamesperse.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://stockist.co/api/v1/u8774/locations/all.js"
    search_res = session.get(search_url, headers=headers)

    stores_list = json.loads(search_res.text)

    for store in stores_list:

        page_url = "<MISSING>"
        locator_domain = website

        location_name = store["name"]

        street_address = store["address_line_1"]
        if (
            "address_line_2" in store
            and store["address_line_2"] is not None
            and len(store["address_line_2"]) > 0
        ):
            street_address = street_address + ", " + store["address_line_2"]

        city = store.get("city", "<MISSING>")
        state = store.get("state", "<MISSING>")
        zip = store.get("postal_code", "<MISSING>")

        country_code = store.get("country", "<MISSING>")

        store_number = store["id"]

        phone = store["phone"]

        location_type = "<MISSING>"

        hours_of_operation = "; ".join(store["description"].split("\n")).strip()
        latitude = store["latitude"]
        longitude = store["longitude"]

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
