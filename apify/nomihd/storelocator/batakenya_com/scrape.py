# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "batakenya.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://batakenya.com/backtoschool",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get("https://batakenya.com/api/chatshops", headers=headers)
        stores = json.loads(stores_req.text)["data"]
        for store in stores:

            store_number = store["id"]
            page_url = "https://batakenya.com/shops/" + store["slug"]
            locator_domain = website

            location_name = store["name"]

            street_address = "<MISSING>"

            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "KE"
            phone = store["phone"]

            location_type = "<MISSING>"
            hours_of_operation = ""
            if "weekdays" in store:
                hours_of_operation = "Mon - Sat:" + store["weekdays"]

            if "weekend" in store:
                hours_of_operation = (
                    hours_of_operation + "; " + "Sunday:" + store["weekend"]
                )

            latitude = "<MISSING>"
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
