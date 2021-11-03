# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "bullritos.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "http://www.bullritos.com/find-a-location/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="section-wrapper"]//h3/a/@href')
    for store_url in stores:
        page_url = store_url
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//meta[@property="og:title"][1]/@content')
        ).strip()

        street_address = "".join(
            store_sel.xpath(
                '//meta[@property="business:contact_data:street_address"][1]/@content'
            )
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//meta[@property="business:contact_data:locality"][1]/@content'
            )
        ).strip()
        state = "".join(
            store_sel.xpath(
                '//meta[@property="business:contact_data:region"][1]/@content'
            )
        ).strip()
        zip = "".join(
            store_sel.xpath(
                '//meta[@property="business:contact_data:postal_code"][1]/@content'
            )
        ).strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        phone = "".join(
            store_sel.xpath(
                '//meta[@property="business:contact_data:phone_number"][1]/@content'
            )
        ).strip()

        hours_of_operation = "<MISSING>"
        store_number = "<MISSING>"

        latitude = "".join(
            store_sel.xpath('//meta[@property="place:location:latitude"][1]/@content')
        ).strip()
        longitude = "".join(
            store_sel.xpath('//meta[@property="place:location:longitude"][1]/@content')
        ).strip()

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
