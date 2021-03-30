# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "castle.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://locator.castle.ca/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("locations = ")[1].strip().split("}};")[0].strip() + "}}"
    )

    for key in stores.keys():
        page_url = "<MISSING>"
        locator_domain = website
        location_name = stores[key]["name"]
        street_address = stores[key]["address"]
        if stores[key]["address2"] is not None and len(stores[key]["address2"]) > 0:
            street_address = street_address + ", " + stores[key]["address2"]

        city = stores[key]["city"]
        state = stores[key]["province"]
        zip = stores[key]["postal_code"]

        country_code = stores[key]["country"]

        store_number = stores[key]["id"]
        phone = stores[key]["phone"]
        if phone == "-":
            phone = "<MISSING>"

        location_type = "<MISSING>"

        hours_list = []
        hours = stores[key]["hours"]
        for hour in hours:
            day = hour["type"]
            time = hour["hours"]
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = stores[key]["lat"]
        longitude = stores[key]["lng"]

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
