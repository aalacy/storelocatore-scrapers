# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "seattlechukis.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.seattlechukis.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.kellysroastbeef.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    api_url = "https://cdn5.editmysite.com/app/store/api/v16/editor/users/131247265/sites/210031257517575645/store-locations?page=1&per_page=100&include=address&lang=en&valid=1"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res["data"]

    for store in stores_list:

        page_url = "https://www.seattlechukis.com/s/order?location=" + store["id"]

        store_number = store["id"]
        locator_domain = website

        location_name = store["display_name"]
        store_info = store["address"]["data"]

        street_address = store_info["street"].strip()
        if "street2" in store_info and store_info["street2"]:
            street_address = (street_address + ", " + store_info["street2"]).strip()

        city = store_info["city"].strip()
        state = store_info["region_code"].strip()

        zip = store_info["postal_code"].strip()

        country_code = store_info["country_code"].strip()
        phone = store_info["phone"]

        location_type = "<MISSING>"

        hours_info = store["pickup_hours"]
        hours = []
        for day in [
            "MON",
            "TUE",
            "WED",
            "THU",
            "FRI",
            "SAT",
            "SUN",
        ]:
            opens = hours_info[day][0]["open"]
            closes = hours_info[day][0]["close"]
            hours.append(f"{day}: {opens}-{closes}")
        hours_of_operation = "; ".join(hours)

        latitude = store_info["latitude"]
        longitude = store_info["longitude"]

        raw_address = "<MISSING>"
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
