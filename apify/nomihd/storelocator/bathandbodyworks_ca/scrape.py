# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "www.bathandbodyworks.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.bathandbodyworks.ca/en/store-locator#/"
    api_url = "https://www.bathandbodyworks.ca/on/demandware.store/Sites-BBW_CA-Site/en_CA/StoreLocator-GetPlacesByLatLng?lat=56.130366&lng=-106.346771&unit=km&radius=9999&countryCode=CA"

    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(api_res.text)
    stores = json_res

    for store in stores:

        page_url = search_url

        location_name = store["storeName"]
        location_type = "<MISSING>"

        locator_domain = website
        raw_address = "<MISSING>"

        street_address = store["address1"]
        if store["address2"] and store["address2"] is not None:
            street_address = (street_address + ", " + store["address2"]).strip()

        city = store["city"]

        state = store["stateCode"]
        zip = store["postalCode"]

        country_code = store["countryCode"]

        store_number = store["id"]

        phone = store["phone"]

        hours_of_operation = (
            store["storeHoursHtml"]
            .replace("%3Cbr%3E", "; ")
            .replace("%20", " ")
            .replace("day", "day:")
            .replace(" ;", ";")
            .strip()
        )
        if "Temporarily Closed" in hours_of_operation:
            location_type = "Temporarily Closed"
            hours_of_operation = "<MISSING>"

        latitude, longitude = (
            store["lat"],
            store["lng"],
        )

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
