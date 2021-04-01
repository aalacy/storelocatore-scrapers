# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "lkbennett.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.lkbennett.com/store-finder?q=%2CGB&page={}"
    page_no = 0
    while True:
        stores_req = session.get(search_url.format(str(page_no)), headers=headers)
        stores = json.loads(stores_req.text)["data"]
        if len(stores) <= 0:
            break

        for store in stores:
            page_url = "<MISSING>"
            location_type = "<MISSING>"
            location_name = store["name"]

            locator_domain = website

            street_address = store["line1"]
            if "line2" in store and len(store["line2"]) > 0:
                street_address = street_address + ", " + store["line2"]
            city = store["town"]
            state = "<MISSING>"
            zip = store["postcode"]
            country_code = "GB"

            phone = store["telephoneNumber"]

            hours_of_operation = ""
            hours = store["openingHours"]
            hours_list = []
            for hour in hours:
                day = hour["day"]
                time = hour["openingTime"]
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            store_number = "<MISSING>"

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

        page_no = page_no + 1


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
