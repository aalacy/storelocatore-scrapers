# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "taza.com.sa"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.taza.com.sa",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.taza.com.sa/en/content/store-locator",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.taza.com.sa/en/content/store-locator"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(
            "https://www.taza.com.sa/en/store-list/", headers=headers
        )
        stores = json.loads(stores_req.text)["stores"]
        for store in stores:
            store_info = store["store"]
            page_url = search_url
            locator_domain = website
            location_name = store_info["name"]
            street_address = store_info["street"]
            if (
                ".street" == street_address
                or "." == street_address
                or "street" == street_address
            ):
                street_address = "<MISSING>"

            city = store_info["location"].split(",")[0].strip()
            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = "SA"
            store_number = store_info["nid"]

            phone = store_info["telephone"]

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude = store_info["lat"]
            longitude = store_info["lon"]
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
