# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "callaffordable.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.callaffordable.com/locations.aspx"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//td[@class="subPrimaryTextCell"]')
    for store in stores:
        page_url = search_url
        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(store.xpath('h2[@itemprop="name"]/text()')).strip()

        street_address = "".join(
            store.xpath(
                'div/div[@itemprop="address"]/span[@itemprop="streetAddress"]/text()'
            )
        ).strip()
        city = "".join(
            store.xpath(
                'div/div[@itemprop="address"]/span[@itemprop="addressLocality"]/text()'
            )
        ).strip()
        state = "".join(
            store.xpath(
                'div/div[@itemprop="address"]/span[@itemprop="addressRegion"]/text()'
            )
        ).strip()
        zip = "".join(
            store.xpath(
                'div/div[@itemprop="address"]/span[@itemprop="postalCode"]/text()'
            )
        ).strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        phone = "".join(store.xpath('.//td[@itemprop="telephone"]/text()')).strip()

        hours_of_operation = "; ".join(
            store.xpath('.//meta[@itemprop="openingHours"]/@content')
        ).strip()
        store_number = "<MISSING>"

        latitude = "".join(
            store.xpath('div[@itemprop="geo"]/meta[@itemprop="latitude"]/@content')
        ).strip()
        longitude = "".join(
            store.xpath('div[@itemprop="geo"]/meta[@itemprop="longitude"]/@content')
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
