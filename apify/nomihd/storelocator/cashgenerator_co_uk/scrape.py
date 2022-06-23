# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "cashgenerator.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Origin": "https://cashgenerator.co.uk",
    "Referer": "https://cashgenerator.co.uk/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    search_url = "https://cashgentestenv.azurewebsites.net/api/allstores"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        stores = json.loads(search_res.text)

        for store in stores:

            page_url = store["slug"].replace("pages/derby-", "pages/derby")
            log.info(page_url)

            locator_domain = website
            location_name = store["title"]
            if (
                "test store" in location_name.lower()
                or "testram" in location_name.lower()
            ):
                continue

            street_address = store["line1"]
            if len(street_address) > 0 and street_address.isdigit():
                street_address = street_address + " " + store["line2"]

            if len(street_address) > 0 and (
                street_address == "Unit 1"
                or street_address == "Unit 50"
                or street_address == "Unit 2 TEST"
                or street_address == "Unit 36"
            ):
                street_address = (
                    street_address.replace("TEST", "").strip() + ", " + store["line2"]
                )

            city = store["town"]
            if not city:
                city = location_name
            state = "<MISSING>"
            zip = store["postCode"]
            if zip and zip == "Peterborough PE1 1EL":
                zip = "PE1 1EL"
                city = "Peterborough"

            country_code = "GB"

            store_number = store["storeId"]
            phone = store["telephone"]

            location_type = "<MISSING>"

            latitude, longitude = store["latitude"], store["longitude"]
            hours_of_operation = store["openHours"].replace("\n", "; ").strip()

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
