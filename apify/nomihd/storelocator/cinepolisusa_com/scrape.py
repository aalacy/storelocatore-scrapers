# -*- coding: utf-8 -*-
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import sglog
import lxml.html
import us
from sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "cinepolisusa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():
    # Your scraper here

    search_url = "https://cinepolisusa.com/locations"
    with SgChrome() as driver:
        driver.get(search_url)

        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath(
            '//div[@class="col-md-12 room_bg_light compact_width_room"]//h2/a/@href'
        )
        for store_url in stores:
            page_url = "https://cinepolisusa.com" + store_url
            locator_domain = website
            log.info(page_url)
            driver.get(page_url)
            store_sel = lxml.html.fromstring(driver.page_source)

            location_name = "".join(
                store_sel.xpath(
                    '//section[@class="white_section no-bottom-padding"]//div[@class="section_header overlay"]/h1/text()'
                )
            ).strip()

            address = "".join(
                store_sel.xpath(
                    '//section[@class="white_section no-bottom-padding"]//div[@class="section_header overlay"]/p/a[@target="_blank"]/text()'
                )
            ).strip()

            street_address = ", ".join(address.split(",")[:-2]).strip()
            city = address.split(",")[-2].strip()
            state = address.split(",")[-1].strip()
            zip = "<MISSING>"

            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath(
                    '//section[@class="white_section no-bottom-padding"]//div[@class="section_header overlay"]/p/a[contains(@href,"tel:")]/text()'
                )
            ).strip()

            location_type = "<MISSING>"
            if "temporarily closed" in driver.page_source.lower():
                location_type = "temporarily closed"

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
