# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "unifac.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "unitedfacilities.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.unifac.com"
    search_url = "https://www.unifac.com/locations"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        stores = json.loads(
            search_res.text.split("var locations = ")[1].strip().split("}];")[0].strip()
            + "}]"
        )

        for store in stores:

            page_url = "https://unitedfacilities.com/locations/profile/" + store["slug"]

            locator_domain = website
            location_name = store["title"]

            street_address = store["address_1"]
            if store["address_2"] is not None and len(store["address_2"]) > 0:
                street_address = street_address + ", " + store["address_2"]

            city = store["city"]
            state = store["state"]
            zip = store["zip"]
            country_code = "US"

            store_number = store["id"]
            phone = store["phone"]

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            latitude, longitude = store["latitude"], store["longitude"]

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
