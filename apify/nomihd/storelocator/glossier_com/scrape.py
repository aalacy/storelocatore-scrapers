# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "glossier.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(verify_ssl=False)
headers = {
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.glossier.com/locations"
    search_res = session.get(search_url, headers=headers)
    json_str = (
        search_res.text.split('JSON.parse("')[1]
        .strip()
        .split('");')[0]
        .strip()
        .replace('\\"', '"')
        .replace('\\\\"', "'")
    )
    stores = json.loads(json_str, strict=False)["data"]["locationsData"][
        "locationsCollection"
    ]["items"]
    for store in stores:
        page_url = search_url
        locator_domain = website

        store_info = store["description"]
        location_name = store_info.split("\\n")[0].strip().replace("__", "").strip()
        if "Opening" in location_name:
            continue

        raw_address = (
            store_info.split(location_name)[1]
            .strip()
            .split("*Credit")[0]
            .strip()
            .replace("__", "")
            .strip()
            .replace("\\n", "")
            .strip()
            .replace("<br>", "")
            .strip()
        )
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"
        if "London" in raw_address:
            country_code = "GB"

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = (
            store_info.split("Hours:")[1]
            .strip()
            .split("\\n<br>\\n<br>\\n")[0]
            .strip()
            .split("\\n<br>", 1)[1]
            .strip()
            .replace("\\n<br>", ";")
            .replace("\\n", "")
            .strip()
            .replace("<br>", "")
            .strip()
        )
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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
