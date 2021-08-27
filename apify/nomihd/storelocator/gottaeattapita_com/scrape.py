# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "gottaeattapita.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "cdn5.editmysite.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "origin": "https://www.gottaeattapita.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.gottaeattapita.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://cdn5.editmysite.com/app/store/api/v17/editor/users/131670744/sites/805011674820655899/store-locations?page=1&per_page=100&include=address&lang=en&valid=1"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["data"]
    for store in stores:
        page_url = "https://www.gottaeattapita.com/locations"

        locator_domain = website

        street_address = store["address"]["data"]["street"]
        if "street2" in store["address"]["data"]:
            if (
                store["address"]["data"]["street2"] is not None
                and len(store["address"]["data"]["street2"]) > 0
            ):
                street_address = (
                    street_address + ", " + store["address"]["data"]["street2"]
                )

        city = store["address"]["data"]["city"]
        state = store["address"]["data"]["region_code"]
        zip = store["address"]["data"]["postal_code"]

        country_code = store["address"]["data"]["country_code"]
        location_name = city + ", " + state

        store_number = store["address"]["data"]["id"]
        phone = store["address"]["data"]["phone"]

        location_type = "<MISSING>"
        hours_list = []
        if "square_business_hours" in store:
            hours = json.loads(store["square_business_hours"])["periods"]
            for hour in hours:
                day = hour["day_of_week"]
                time = hour["start_local_time"] + " - " + hour["end_local_time"]
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store["address"]["data"]["latitude"]
        longitude = store["address"]["data"]["longitude"]

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
