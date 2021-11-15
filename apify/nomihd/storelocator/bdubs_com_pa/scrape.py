# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "bdubs.com.pa"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "http://www.bdubs.com.pa/ubicaciones/?"
    search_res = session.get(
        "http://www.bdubs.com.pa/assets/locations.json", headers=headers
    )

    store_list = json.loads(search_res.text)["Markers"]

    for store in store_list:
        store_json = store["Store_Data"]
        page_url = search_url

        locator_domain = website

        full_address = store_json["Address"].split("<br>")

        street_address = ", ".join(full_address[:-1]).strip()
        city = full_address[-1].strip()
        state = "<MISSING>"
        zip = "<MISSING>"
        country_code = "PA"

        location_name = store_json["Name"]

        store_number = store["id"]

        location_type = "<MISSING>"
        phone = store_json["PhoneNumber"]
        if phone and "," in phone:
            phone = phone.split(",")[0].strip()

        hours = store_json["StoreHours"]
        hours_of_operation = "<MISSING>"
        if hours:
            hours_of_operation = "; ".join(hours).strip()

        latitude, longitude = store_json["Latitude"], store_json["Longitude"]

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
