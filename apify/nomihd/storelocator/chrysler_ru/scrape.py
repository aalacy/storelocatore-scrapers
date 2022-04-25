# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "chrysler.ru"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    api_url = "https://cjd-dealers.supportix.ru/dealer/dealer_json.php?brand_id=4&callback=jsonCallback"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)
        json_str = (
            api_res.text.split("jsonCallback(")[1]
            .strip()
            .split("]);")[0]
            .strip()
            .replace(' "\\u0', " '\\u0")
            .replace('""', "'\"")
            .replace("'\",", '"",')
            + "]"
        )
        stores = json.loads(json_str)
        for store in stores:

            locator_domain = website

            location_name = store["dealer_name_en"]
            page_url = "https://www.jeep-russia.ru/dealers"

            location_type = "<MISSING>"

            raw_address = store["dealer_adress_en"]
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = store["dealer_region_name_en"]
            state = "<MISSING>"
            zip = store["dealer_pindex"]

            country_code = "RU"

            if store["dealer_phone"]:

                phone = store["dealer_phone"][0]
            else:
                phone = "<MISSING>"
            hours_of_operation = "<MISSING>"

            store_number = store["id"]

            latitude, longitude = store["dealer_latitude"], store["dealer_longitude"]

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
