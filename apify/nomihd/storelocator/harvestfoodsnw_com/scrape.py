# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "harvestfoodsnw.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    seacrh_url = "https://www.harvestfoodsnw.com/find-your-store/location-map/?group=or"

    seacrh_res = session.get(seacrh_url, headers=headers)
    locations = (
        "["
        + seacrh_res.text.split("var stores = [")[1]
        .split("// Map variables")[0]
        .strip()[:-1]
    )
    stores_list = json.loads(locations)

    for store in stores_list:

        locator_domain = website

        location_name = store["name"].strip()
        street_address = store["address1"].strip()
        city = store["city"].strip()
        state = store["state"].strip()

        page_url = f"https://www.harvestfoodsnw.com/find-your-store/location-map/?group={state.lower()}"
        log.info(page_url)
        zip = store["zipCode"].strip()
        country = "US"
        country_code = country

        store_number = store["storeID"]

        phone = store["storeInfo"].strip().split("\n")[-1].strip()

        location_type = "<MISSING>"

        hours_of_operation = store["hourInfo"] if "hourInfo" in store else "<MISSING>"

        if "<b>" in hours_of_operation:
            hours_of_operation = "<MISSING>"

        hours_of_operation = hours_of_operation.replace("Store Hours:", "").strip()
        latitude = store["latitude"]
        longitude = store["longitude"]

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
