# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "kurtgeiger.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://live-svc-storesinfo.kurtgeiger.com/LATEST/stores/isEnabled/1"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)
    for store_json in stores:
        if (
            store_json["type"].lower().strip() == "store"
            or store_json["type"].lower().strip() == "internal"
        ):
            page_url = "https://www.kurtgeiger.com/storelocator"

            latitude = store_json["latitude"]
            longitude = store_json["longitude"]

            location_name = store_json["name"].upper()

            locator_domain = website

            location_type = store_json["type"]

            street_address = store_json["streetLine1"]
            if (
                store_json["streetLine2"] is not None
                and len(store_json["streetLine2"]) > 0
            ):
                street_address = street_address + ", " + store_json["streetLine2"]

            if (
                store_json["streetLine3"] is not None
                and len(store_json["streetLine3"]) > 0
            ):
                street_address = street_address + ", " + store_json["streetLine3"]

            city = store_json["town"]
            state = "<MISSING>"
            zip = store_json["postcode"]
            if zip and zip == "N/A":
                zip = "<MISSING>"
            country_code = store_json["country"]
            phone = store_json["phone"]
            hours_of_operation = ""
            hours_list = []
            hours = store_json["openingHours"]
            for hour in hours:
                day = hour["day"]
                time = ""
                if hour["isClosed"] == 1:
                    time = "Closed"
                    hours_list.append(day + ":" + time)
                else:
                    if len(hour["openingTime"]) > 0 and len(hour["closingTime"]) > 0:
                        time = hour["openingTime"] + "-" + hour["closingTime"]
                        hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            store_number = str(store_json["id"])
            if len(street_address) <= 0:
                continue
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
