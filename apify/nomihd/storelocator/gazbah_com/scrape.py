# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "gazbah.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.gazbah.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//tbody[@class="row-hover"]/tr')
    for store in stores:
        page_url = search_url
        location_type = "".join(store.xpath("td[2]/text()")).strip()
        locator_domain = website
        location_name = "GAZBAH"

        street_address = "".join(store.xpath("td[3]/text()")).strip()
        city = "".join(store.xpath("td[4]/text()")).strip()
        state = "".join(store.xpath("td[5]/text()")).strip()
        zip = "<MISSING>"
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        phone = "".join(store.xpath("td[6]/text()")).strip()

        hours_of_operation = (
            "".join(store.xpath("td[8]/text()")).strip()
            + " - "
            + "".join(store.xpath("td[9]/text()")).strip()
        )
        store_number = "".join(store.xpath("td[1]/text()")).strip()

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
