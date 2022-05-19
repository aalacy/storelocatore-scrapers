# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal import sgpostal as parser

website = "bitcoin4u.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "cdn.storelocatorwidgets.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = (
        "https://cdn.storelocatorwidgets.com/json/1072950dea7de5d0fa3f12fd8dd742e5"
    )
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(
            stores_req.text.split("slw(")[1].strip().rsplit(")", 1)[0].strip()
        )["stores"]

        for store_json in stores:
            page_url = store_json["data"]["website"]

            location_name = store_json["name"]
            location_type = "<MISSING>"
            locator_domain = website

            raw_address = store_json["data"]["address"]
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            if not zip:
                if page_url == "https://bitcoin4u.ca/atm/north-york-3/":
                    zip = "M2J 2K8"

            country_code = "CA"
            store_number = store_json["storeid"]
            phone = store_json["data"]["phone"]
            hours_list = []
            for key in store_json["data"].keys():
                if "hours_" in key:
                    day = key.replace("hours_", "").strip()
                    time = store_json["data"][key]
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store_json["data"]["map_lat"]
            longitude = store_json["data"]["map_lng"]

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
