# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "shoelessjoes.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    api_url = "https://www.shoelessjoes.ca/core/assets/shoelessjoes/locations.json"
    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)

        json_res = json.loads(api_res.text)

        stores_list = json_res["locations"]

        for store in stores_list:

            page_url = store["detailPageLink"].strip()
            locator_domain = website

            location_name = store["title"].strip()
            raw_address = store["addressDetails"]["entry"].strip().replace("\n", " ")

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "CA"
            store_number = "<MISSING>"

            phone = store["addressDetails"]["phoneLine"]

            location_type = "<MISSING>"
            if "Opening" in location_name:
                location_type = "opening soon"

            hours_info = store["schedule"]
            if hours_info:
                hours_list = []

                for day, timing in hours_info.items():
                    hours_list.append(f"{day.strip()}: {timing}")

                hours_of_operation = "; ".join(hours_list)

            else:
                hours_of_operation = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]

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
