# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "rent1st.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    api_url = "https://rent1st.com/?hcs=locatoraid&hca=search%3Asearch%2F%2Fproduct%2F_PRODUCT_%2Flat%2F%2Flng%2F%2Flimit%2F100"
    api_res = session.get(api_url, headers=headers)
    json_obj = json.loads(api_res.text)

    store_list = json_obj["results"]

    for store in store_list:

        page_url = "https://rent1st.com/locations/"
        locator_domain = website

        location_name = store["name"].strip()
        street_address = store["street1"].strip()

        if "street2" in store and store["street2"] is not None:
            street_address = (street_address + ", " + store["street2"]).strip(", ")

        city = store["city"].strip()

        state = store["state"].strip()
        zip = store["zip"].strip()

        country_code = "US"

        store_number = store["id"]

        phone = store["phone"].split('"_blank">')[1].strip(" </a>")

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = store["latitude"].strip()
        longitude = store["longitude"].strip()

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
