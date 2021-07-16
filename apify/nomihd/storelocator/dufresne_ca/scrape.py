# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "dufresne.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=dufresne-furniture-appliances.myshopify.com&latitude=48.4086156&longitude=-89.2605615&max_distance=0&limit=100000"
    search_res = session.get(search_url, headers=headers)

    stores_list = json.loads(search_res.text)["stores"]

    for store in stores_list:

        page_url = store["5"]
        locator_domain = website

        location_name = store["name"]

        street_address = store["address"]

        if (
            "address2" in store
            and store["address2"] is not None
            and len(store["address2"]) > 0
        ):
            street_address = street_address + ", " + store["address2"]

        city = store["city"]
        state = store["prov_state"]
        zip = store["postal_zip"]

        country_code = store["country"]

        store_number = store["store_id"]

        phone = store["phone"]

        location_type = "<MISSING>"

        hours_of_operation = (
            "; ".join(store["hours"].split("\r\n"))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        latitude = store["lat"]
        longitude = store["lng"]

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
