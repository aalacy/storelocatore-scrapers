# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bushschicken.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "http://www.bushschicken.com/locations/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        tables = stores_sel.xpath('//div[@class="content"]/table')
        table_headers = stores_sel.xpath('//div[@class="content"]/h3/text()')
        for index in range(0, len(table_headers)):
            location_type = table_headers[index].strip()
            if len("".join(location_type).strip()) <= 0:
                continue
            stores = tables[index].xpath(".//tr")
            for store in stores:
                if len("".join(store.xpath("td[1]/text()")).strip()) > 0:
                    page_url = search_url
                    locator_domain = website
                    location_name = "BUSH'S CHICKEN"
                    street_address = "".join(store.xpath("td[2]/text()")).strip()
                    city = "".join(store.xpath("td[1]/text()")).strip()
                    state = "".join(store.xpath("td[3]/text()")).strip()
                    zip = "".join(store.xpath("td[4]/text()")).strip()

                    country_code = "<MISSING>"
                    if us.states.lookup(state):
                        country_code = "US"

                    store_number = "<MISSING>"
                    phone = "".join(store.xpath("td[5]/text()")).strip()

                    hours_of_operation = "<MISSING>"
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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
