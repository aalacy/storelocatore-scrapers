# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "shopwss.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://cdn.shopify.com/s/files/1/0069/3442/9751/t/11/assets/sca.storelocatordata.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:
        if "description" in store and "opening" in store["description"].lower():
            continue
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["name"]
        store_number = store["name"].split("-")[0].replace("Store", "").strip()

        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip = store["postal"]
        if zip and zip.isalpha():
            zip = "<MISSING>"
        country_code = store["country"]

        phone = store["phone"]

        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = "<MISSING>"
        if "schedule" in store:
            hours_of_operation = "; ".join(store["schedule"].split("\r<br>")).strip()

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
