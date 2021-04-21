# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "bruchis.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "http://www.bruchis.com/index.php?plugin=locations&action=locations_ajax_map&lat=47.6728404&lon=-117.4121499&radius=10000"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text, strict=False)
    for store in stores:
        page_url = "http://www.bruchis.com/locations/" + store["info"]["permalink"]

        locator_domain = website
        location_name = store["info"]["location"]
        street_address = store["info"]["address"]
        city = store["info"]["city"]
        state = store["info"]["state"]
        zip = store["info"]["zip"]
        country_code = "US"

        phone = store["info"]["phone"]

        store_number = store["info"]["id"]
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"
        latitude = store["info"]["lat"]
        longitude = store["info"]["lng"]

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
