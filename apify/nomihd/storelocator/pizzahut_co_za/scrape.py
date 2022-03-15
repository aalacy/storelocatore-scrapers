# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "pizzahut.co.za"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.pizzahut.co.za",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "franchiseid": "14",
    "longitude": "",
    "content-type": "application/json",
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "latitude": "",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahut.co.za/api/stores"

    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["Data"]
    for store in stores:
        if store["active"] != "1":
            continue
        page_url = "https://pizzahut.com.tr/restoranlar"
        location_name = store["name"]
        location_type = "<MISSING>"
        locator_domain = website
        street_address = store["address1"]
        if store["address2"]:
            street_address = street_address + ", " + store["address2"]

        city = store["city"]
        state = store["state"]
        zip = store["zipcode"]
        if zip and zip == "0":
            zip = "<MISSING>"

        country_code = store["country"]
        store_number = store["store_id"]
        phone = store["phone"]
        hours_list = []
        hours = store["operatinghours"]
        for hour in hours:
            if hour["channel"] == "Delivery":
                day = hour["day"]
                time = hour["start_time"] + " - " + hour["close_time"]
                hours_list.append(day + ": " + time)

        hours_of_operation = "; ".join(hours_list).strip()

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
