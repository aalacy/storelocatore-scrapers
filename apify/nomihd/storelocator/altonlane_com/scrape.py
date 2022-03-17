# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "altonlane.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    api_url = "https://www.altonlane.com/b2c/services/StoreLocator.Service.ss?c=3556903&latitude=40.75368539999999&locationtype=1&longitude=-73.9991637&n=3&page=all&radius=100000&sort=distance"
    api_res = session.get(api_url, headers=headers)
    stores_list = json.loads(api_res.text)

    for store in stores_list:

        page_url = (
            f'https://www.altonlane.com/stores/details/{store["internalid"].strip()}'
        )
        log.info(page_url)
        locator_domain = website
        location_name = store["name"].strip()

        street_address = store["address1"].strip()
        if (
            "address2" in street_address
            and store["address2"] is not None
            and len(store["address2"]) > 0
        ):
            street_address = street_address + ", " + store["address2"]

        city = store["city"].strip()
        state = store["state"].strip()
        zip = store["zip"].strip()

        country_code = store["country"].strip()

        store_number = store["internalid"].strip()
        phone = store["phone"].strip()

        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        latitude = store["location"]["latitude"]
        longitude = store["location"]["longitude"]

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
