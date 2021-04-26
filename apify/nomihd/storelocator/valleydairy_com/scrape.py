# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "valleydairy.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.valleydairy.com/location-list"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//section[@id="content"]/ul/li/a/@href')

    for store_url in stores:
        page_url = "https://www.valleydairy.com" + store_url
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//h1[@itemprop="headline  name"]/text()')
        ).strip()

        address = store_sel.xpath('//section[@id="content"]/p[2]/text()')
        street_address = "; ".join(address[:-1]).strip()
        city = address[-1].split(",")[0].strip()
        state = address[-1].split(",")[1].strip().split(" ")[0].strip()
        zip = address[-1].split(",")[1].strip().split(" ")[-1].strip()
        country_code = "US"

        phone = (
            "".join(
                store_sel.xpath(
                    '//section[@id="content"]/p[contains(text(),"Phone")]/text()'
                )
            )
            .strip()
            .replace("Phone:", "")
            .strip()
        )

        store_number = "<MISSING>"
        if "#" in location_name:
            store_number = location_name.split("#")[1].strip()
        location_type = "<MISSING>"

        hours_of_operation = "; ".join(
            store_sel.xpath('//section[@id="content"]/ul/li/text()')
        ).strip()
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
