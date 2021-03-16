# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "enterprisebank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.enterprisebank.com/modules/multilocation/?within_business=true&offset=0&business_id=478395&limit=20000&published=1&threshold=20000&near_location=10001&services__in="
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["objects"]
    for store in stores:
        page_url = store["location_url"]
        location_type = "<MISSING>"
        locator_domain = website
        location_name = store["location_name"]

        street_address = store["street"]
        if store["street2"] is not None and len(store["street2"]) > 0:
            street_address = street_address + ", " + store["street2"]

        city = store["city"]
        state = store["state"]
        zip = store["postal_code"]
        country_code = store["country"]
        phone = store["phonemap"]["phone"]

        hours_of_operation = "<MISSING>"
        hours = store["formatted_hours"]["primary"]["days"]
        hours_list = []
        for hour in hours:
            day = hour["label"]
            time = hour["content"]
            if len(day) > 0:
                hours_list.append(day + ":" + time)

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        store_number = store["id"]

        latitude = store["lat"]
        longitude = store["lon"]

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
