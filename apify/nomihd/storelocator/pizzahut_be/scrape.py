# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.be"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "*/*",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://restaurants.pizzahut.be/api/stores"
    search_res = session.get(search_url, headers=headers)
    stores = json.loads(search_res.text)
    for store in stores:
        page_url = "https://restaurants.pizzahut.be" + store["view_node"]
        log.info(page_url)
        store_req = session.get(
            f"https://www.pizzahut.be/nl/ajax/store/{store['id']}", headers=headers
        )
        store_json = json.loads(store_req.text)["store"]

        locator_domain = website

        location_name = store_json["name"]

        street_address = store_json["address1"]
        if store_json["address2"] is not None and len(store_json["address2"]) > 0:
            street_address = street_address + ", " + store_json["address2"]

        city = store_json["city"]
        state = store_json["region"]
        zip = store_json["postcode"]

        country_code = store_json["country"]

        phone = store_json["phone"]

        store_number = store_json["code"]

        location_type = "<MISSING>"

        hours = store_json["openingsHours"]
        hours_list = []
        for hour in hours:
            day = hour["dayName"]
            time = hour["shift1"].replace("/", " - ").strip()
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store_json["latitude"]
        longitude = store_json["longitude"]

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
