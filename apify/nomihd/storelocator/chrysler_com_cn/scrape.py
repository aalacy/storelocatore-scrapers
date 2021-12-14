# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "chrysler.com.cn"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    api_url = "http://www.chrysler.com.cn/js/dealer_data.js"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)
        json_str = api_res.text.split("let dealerData =")[1].strip()
        json_res = json.loads(json_str)
        stores = json_res

        for store in stores:

            locator_domain = website

            location_name = store["name"]
            page_url = "<MISSING>"

            location_type = "<MISSING>"

            raw_address = store["address"]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = store["city"]
            state = store["province"]
            zip = formatted_addr.postcode

            country_code = "CN"

            phone = (
                store["phone"]
                .replace("&mdash;", "-")
                .strip()
                .split(";")[0]
                .strip()
                .split("/")[0]
                .strip()
            )
            hours_of_operation = "<MISSING>"

            store_number = store["id"]
            map_info = store["map"]
            if map_info:
                latitude, longitude = map_info.split(",")[0], map_info.split(",")[1]
            else:
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
