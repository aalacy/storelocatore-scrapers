# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "redwingheritage.eu"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.redwingheritage.eu",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "adrum": "isAjax:true",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.redwingheritage.eu/eu/EUR/page/find-a-store",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (
    (
        "SynchronizerToken",
        "c3ca0f2b5741414c27f6712a30e55fd9098a127e6e17e89685f2d0ec51e6b254",
    ),
    ("AjaxRequestMarker", "true"),
)


def fetch_data():
    # Your scraper here
    api_url = "https://www.redwingheritage.eu/INTERSHOP/rest/WFS/RWSC-HeritageEU-Site/-/stores"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        api_res = session.get(api_url, headers=headers, params=params)
        stores = json.loads(api_res.text)["elements"]

        for store in stores:
            locator_domain = website
            location_name = store["storeName"]
            store_number = store["storeId"]
            page_url = store["storeURL"]

            location_type = store["storeType"]

            street_address = store["address1"]
            if "address2" in store and store["address2"] and len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]

            city = store["city"]
            state = store["state"]
            if state and state == "-":
                state = "<MISSING>"

            zip = store["postalCode"]

            country_code = store["country"]
            raw_address = "<MISSING>"
            if country_code == "Japan":
                raw_address = street_address
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = raw_address.split(",")[0].strip()
                city = formatted_addr.city

            phone = store["phone"]

            hours_of_operation = "<MISSING>"

            latitude, longitude = (
                store["latitude"],
                store["longitude"],
            )
            if latitude == 0.0 and longitude == 0.0:
                latitude, longitude = "<MISSING>", "<MISSING>"
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
