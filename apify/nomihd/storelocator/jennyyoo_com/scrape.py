# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "jennyyoo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jennyyoo.com/retailers"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("window.__INITIAL_STATE__=")[1]
        .strip()
        .split("}};")[0]
        .strip()
        + "}}"
    )["siteSettings"]["flagshipStores"]

    for store in stores:

        page_url = search_url
        location_name = store["title"]
        locator_domain = website

        street_address = store["address"]["line1"]
        if "line2" in store["address"]:
            street_address = street_address + ", " + store["address"]["line2"]

        city = store["address"]["city"]
        state = store["address"]["state"]
        zip = store["address"]["zip"]
        country_code = "US"
        store_number = "<MISSING>"
        phone = store["phone"]

        location_type = "<MISSING>"

        hours_of_operation = "; ".join(store["workingHours"].split("\n")).strip()

        latitude = store["address"]["coordinates"]["lat"]
        longitude = store["address"]["coordinates"]["lng"]

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
