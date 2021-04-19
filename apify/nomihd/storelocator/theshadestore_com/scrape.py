# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "theshadestore.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.theshadestore.com/showrooms"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="location"]/a/@href')

    for store_url in stores:
        page_url = "https://www.theshadestore.com" + store_url
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//h1[contains(@class,"hero-dark-copy")]/text()')
        ).strip()

        street_address = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/p[@itemprop="streetAddress"]/text()'
            )
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]//span[@itemprop="addressLocality"]/text()'
            )
        ).strip()
        state = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]//span[@itemprop="addressRegion"]/text()'
            )
        ).strip()
        zip = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]//span[@itemprop="postalCode"]/text()'
            )
        ).strip()

        country_code = "US"
        phone = "".join(
            store_sel.xpath('//div/p[@itemprop="telephone"]/text()')
        ).strip()

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "; ".join(store_sel.xpath('//p[@itemprop="openingHours"]/text()'))
            .strip()
            .replace("\n", "")
            .strip()
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"/maps/embed?")]/@src')
        ).strip()
        if len(map_link) > 0:
            latitude = map_link.split("!1d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
