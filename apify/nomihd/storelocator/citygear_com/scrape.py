# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "citygear.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.hibbett.com",
    "cache-control": "max-age=0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    url = (
        "https://www.hibbett.com/on/demandware.store/Sites-Hibbett-US-Site/"
        "default/Stores-GetNearestStores?latitude=28.14&"
        "longitude=-95.85&countryCode=US&distanceUnit=mi&maxdistance=2500000"
    )
    stores_req = session.get(
        url,
        headers=headers,
    )
    stores = json.loads(stores_req.text.strip())["stores"]
    for store in stores.keys():
        locator_domain = website
        location_name = stores[store]["name"]
        if location_name != "City Gear":
            continue
        street_address = stores[store]["address1"]
        if len(stores[store]["address2"]) > 0:
            street_address = street_address + ", " + stores[store]["address2"]
        city = stores[store]["city"]
        state = stores[store]["stateCode"]
        zip = stores[store]["postalCode"]
        country_code = stores[store]["countryCode"]
        page_url = (
            "https://www.hibbett.com/storedetails/"
            + state
            + "/"
            + city
            + "/"
            + stores[store]["id"]
        )

        phone = stores[store]["phone"]
        store_number = "<MISSING>"

        location_type = "<MISSING>"
        if stores[store]["isOpeningSoon"] is True:
            location_type = "Opening Soon"

        if stores[store]["temporarilyClosed"] is True:
            location_type = "Temporarily Closed"

        latitude = stores[store]["latitude"]
        longitude = stores[store]["longitude"]
        hours_of_operation = stores[store]["storeHours"].replace("|", " ").strip()

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
