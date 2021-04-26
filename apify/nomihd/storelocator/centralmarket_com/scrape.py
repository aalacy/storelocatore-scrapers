# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json

website = "centralmarket.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://centralmarket.com/stores"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath('//div[@class="store "]/a/@href')

    for store in stores_list:

        page_url = search_url
        locator_domain = website

        log.info(store)
        page_res = session.get(store, headers=headers)

        json_str = (
            page_res.text.split(
                '<script type="application/json" data-heb-key="FulfillmentBar"'
            )[1]
            .split("><!--")[1]
            .split("--></script>")[0]
        )
        
        json_res = json.loads(json_str)

        store_obj = json_res["session"]["channels"]["curbside"]["store"]

        location_name = store_obj["address"]["company"].strip()
        street_address = store_obj["address"]["address_1"].strip()

        if (
            "address_2" in store_obj["address"]
            and store_obj["address"]["address_2"] is not None
        ):
            street_address = (
                street_address + ", " + store_obj["address"]["address_2"]
            ).strip(", ")

        city = store_obj["address"]["city"].strip()

        state = store_obj["address"]["state"].strip()
        zip = store_obj["address"]["postcode"].strip()

        country_code = store_obj["address"]["country"].strip()

        store_number = store_obj["id"]

        phone = store_obj["phone"]

        location_type = "<MISSING>"

        hours_of_operation = json_res["session"]["channels"]["curbside"]["schedule"][
            "timeslot"
        ]

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
