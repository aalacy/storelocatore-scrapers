# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "bimbobakeriesusa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://bimbobakeriesusa.com/outlet-locator"
    home_req = session.get(search_url, headers=headers)
    home_sel = lxml.html.fromstring(home_req.text)
    states = home_sel.xpath('//select[@id="outletstore-search-state"]/option/@value')

    for state in states:
        stores_req = session.get(
            "https://bimbobakeriesusa.com/json/bbu_outletlocator_api/stores/" + state,
            headers=headers,
        )
        stores = json.loads(stores_req.text.replace('"', "").replace("\\u0022", '"'))

        for store in stores:
            page_url = "<MISSING>"
            location_type = "<MISSING>"
            locator_domain = website
            location_name = "BIMBO BAKERIES USA"

            street_address = store["street"].replace("\\t", "").strip()
            city = store["city"].replace("\\t", "").strip()
            state = store["state"].replace("\\t", "").strip()
            zip = store["zip"].replace("\\t", "").strip()
            country_code = "US"
            phone = store["phone"].replace("\\t", "").strip()
            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
