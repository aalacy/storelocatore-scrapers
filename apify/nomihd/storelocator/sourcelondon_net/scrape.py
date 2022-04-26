# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "sourcelondon.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.sourcelondon.net/home/map",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Content-Language": "en-GB",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    api_url = "https://www.sourcelondon.net/api/infra/location"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        stores = json.loads(api_res.text)

        for no, store in enumerate(stores, 1):

            locator_domain = website

            location_name = store["name"]

            location_type = "<MISSING>"

            page_url = "https://www.sourcelondon.net/home/map?evseId=" + store["emi3"]

            raw_address = "<MISSING>"

            street_address = location_name

            city = store["address"]["city"]

            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "GB"

            phone = "<MISSING>"

            hours_of_operation = store["openingTimes"]["universalTextualRepresentation"]

            store_number = store["id"]

            latitude, longitude = (
                store["coordinates"]["latitude"],
                store["coordinates"]["longitude"],
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
