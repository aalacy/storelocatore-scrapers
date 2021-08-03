# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thegymgroup.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.thegymgroup.com/findgymmapblock/searchmap/?limit=999"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:
        if store["gym"]["status"] == "Opening Soon":
            continue

        page_url = "https://www.thegymgroup.com" + store["moreInfoUrl"]
        locator_domain = website
        location_name = store["gym"]["name"]

        street_address = (
            store["gym"]["address1"].replace("\r\n", ", ").replace("\n", ", ").strip()
        )
        address2 = store["gym"]["address2"]
        if address2 is not None and len(address2) > 0:
            street_address = (
                street_address
                + ", "
                + address2.replace("\r\n", ", ").replace("\n", ", ").strip()
            )

        street_address = street_address.replace(",,", ",").strip()
        city = ""
        if store["gym"]["city"] is not None:
            city = (
                store["gym"]["city"].replace("\r\n", ", ").replace("\n", ", ").strip()
            )
        state = "<MISSING>"
        zip = store["gym"]["postcode"]
        country_code = "GB"

        store_number = "<MISSING>"
        phone = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"
        latitude = store["gym"]["latitude"]
        longitude = store["gym"]["longitude"]
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
