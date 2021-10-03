# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "greenp.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "parking.greenp.com",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "accept": "application/json",
    "x-requested-with": "XMLHttpRequest",
    "x-request": "JSON",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://parking.greenp.com/find-parking/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    ("api_key", "eedeab41c581e6883cd4eb349fdea8329dc450479b7f686dff292b5bf2de6f5b"),
)


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(
            "https://parking.greenp.com/api/carparks/", headers=headers, params=params
        )
        stores = json.loads(stores_req.text)["carparks"]

        for store in stores:
            page_url = store["slug"]
            locator_domain = website
            location_name = "Carpark"

            phone = "<MISSING>"
            street_address = store["address"]
            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "US"

            store_number = store["id"]
            location_name = location_name + " " + str(store_number)
            location_type = store["carpark_type_str"]
            hours_of_operation = "<MISSING>"
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
