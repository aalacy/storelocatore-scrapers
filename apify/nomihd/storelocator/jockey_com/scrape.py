# -*- coding: utf-8 -*-
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
website = "jockey.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    # Your scraper here
    search_url = "https://www.jockey.com/shoppingguide/storelocator"
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(search_url)
        time.sleep(10)
        stores = json.loads(
            driver.page_source.split("allStores:")[1].strip().split("}]}")[0].strip()
            + "}]"
        )
        for store in stores:
            page_url = search_url
            locator_domain = website
            location_name = store["DisplayName"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["Address"]["Line1"]
            if (
                store["Address"]["Line2"] is not None
                and len(store["Address"]["Line2"]) > 0
            ):
                street_address = street_address + store["Address"]["Line2"]

            city = store["Address"]["City"]
            state = store["Address"]["State"]["Short"]
            zip = store["Address"]["PostalCode"]

            country_code = store["Address"]["Country"]

            store_number = str(store["StoreCode"])
            phone = store["Contact"]["Phone"]

            location_type = "<MISSING>"
            hours_of_operation = "; ".join(store["Hours"]["Display"])

            latitude = store["Address"]["LngLat"][1]
            longitude = store["Address"]["LngLat"][0]

            if phone is None:
                phone = "<MISSING>"

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
