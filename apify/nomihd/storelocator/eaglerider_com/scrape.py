# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "eaglerider.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.eaglerider.com/locations"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        json_str = (
            search_res.text.split("markers:")[1]
            .split("image_paths:")[0]
            .strip()
            .strip(" },")
            .strip()
            .strip(" ,")
            .strip()
        )

        stores = json.loads(json_str)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = "https://www.eaglerider.com" + store["url"]

            location_name = store["name"].strip()

            location_type = "<MISSING>"

            raw_address = "<MISSING>"

            street_address = store["street_address"]

            city = store["city"]

            state = store["state"]

            zip = store["postal_code"]
            country_code = store["country_name"]

            phone = store["phone"]
            hours = store["hours_of_operation"]

            hours_of_operation = "; ".join(hours)

            store_number = store["id"]

            latitude, longitude = store["latitude"], store["longitude"]
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
