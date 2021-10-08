# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgpostal import sgpostal as parser
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "forever21.com.mx"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://forever21.com.mx/pages/store-locator-2"
    api_url = "https://stockist.co/api/v1/u9192/locations/all.js?callback=_stockistAllStoresCallback"

    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(
        api_res.text.split("_stockistAllStoresCallback(")[1].strip("); ")
    )
    stores = json_res

    for store in stores:

        page_url = search_url

        location_name = store["name"]
        page_url = search_url
        location_type = "<MISSING>"
        raw_address = (
            store["address_line_1"].replace("Forever 21 Store", "").strip(" :")
        )

        locator_domain = website

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        if street_address is not None:
            street_address = street_address.replace("Ste", "Suite")
        city = store["city"]
        if not city:
            city = formatted_addr.city
        state = store["state"]
        if not state:
            state = formatted_addr.state
        zip = store["postal_code"]
        if not zip:
            zip = formatted_addr.postcode

        country_code = "MX"

        store_number = store["id"]

        phone = store["phone"]
        if phone:
            phone = phone.split("ext")[0].strip()

        hours_of_operation = store["address_line_2"]
        if hours_of_operation and store["description"]:
            hours_of_operation = hours_of_operation + "; " + store["description"]

        latitude, longitude = (
            store["latitude"],
            store["longitude"],
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
