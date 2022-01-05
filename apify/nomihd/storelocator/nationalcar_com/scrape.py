# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "nationalcar.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.nationalcar.com/en/car-rental/locations.html"
    api_url = "https://prd.location.enterprise.com/enterprise-sls/search/location/national/web/all?cor=US&locale=en_US&dto=true"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)
        json_res = json.loads(api_res.text)

        stores = json_res

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url
            location_name = store["name"]

            location_type = store["location_type"]

            raw_address = "<MISSING>"

            store_info = store["address"]
            street_address = ", ".join(store_info["street_addresses"])
            city = store_info["city"]

            state = store_info["country_subdivision_code"]

            zip = store_info["postal"]

            country_code = store_info["country_code"]

            phone = store["phones"]
            if phone:
                phone = phone[0]["phone_number"]
            else:
                phone = "<MISSING>"

            hours_of_operation = store["hours"]
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            store_number = store["id"]

            latitude, longitude = store["gps"]["latitude"], store["gps"]["longitude"]
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
