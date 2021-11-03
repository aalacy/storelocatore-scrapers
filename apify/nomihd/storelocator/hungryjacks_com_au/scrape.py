# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "hungryjacks.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.hungryjacks.com.au",
    "content-length": "0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "origin": "https://www.pizzahutcr.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.pizzahutcr.com/index/encuentrarestaurante",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    base = "https://www.hungryjacks.com.au"
    api_url = "https://www.hungryjacks.com.au/api/storelist"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    store_list = json_res

    for store in store_list:

        page_url = base + store["storeUrl"]
        locator_domain = website

        raw_address = "<MISSING>"

        street_address = store["location"]["address"]
        city = store["location"]["suburb"]
        state = store["location"]["state"]
        zip = store["location"]["postcode"]

        country_code = "AU"

        location_name = store["name"]

        phone = store["location"]["phone"].split("[")[0].strip()
        store_number = store["store_id"]

        location_type = "<MISSING>"

        hour_list = []
        for day in store["hours"]["dine_in"]:
            if day["is_open"]:
                hour_list.append(f"{day['day_name']}: {day['open']} - {day['close']}")
            else:
                hour_list.append(f"{day['day_name']}: Closed")
        hours_of_operation = "; ".join(hour_list)

        latitude, longitude = (
            store["location"]["lat"],
            store["location"]["long"],
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
