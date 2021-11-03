# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgselenium import SgChrome
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "ocmattress.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def fetch_data():
    # Your scraper here

    search_url = "https://www.ocmattress.com/pages/store-locator"

    with SgChrome() as driver:
        driver.get(search_url)
        time.sleep(30)
        search_sel = lxml.html.fromstring(driver.page_source)

        stores_list = search_sel.xpath('//ul[@class="list"]/li')

        for store in stores_list:

            locator_domain = website

            location_name = "".join(
                store.xpath('.//div[contains(@id,"title")]/text()')
            ).strip()

            page_url = (
                "https://www.ocmattress.com/pages/"
                + location_name.lower().replace(" ", "-")
            )

            log.info(page_url)
            store_req = session.get(page_url)
            store_sel = lxml.html.fromstring(store_req.text)

            address_info = list(
                filter(
                    str,
                    store.xpath('.//div[contains(@id,"address")]/text()'),
                )
            )

            street_address = " ".join(address_info).strip()

            city = "".join(store.xpath('.//span[contains(@id,"city")]/text()')).strip()

            state = "".join(
                store.xpath('.//span[contains(@id,"state")]/text()')
            ).strip()
            zip = "".join(
                store.xpath('.//span[contains(@id,"zipcode")]/text()')
            ).strip()
            country_code = "US"

            store_number = "<MISSING>"

            phone = "".join(store.xpath('.//div[contains(@id,"phone")]/text()')).strip()

            if not phone:
                phone = "".join(
                    store_sel.xpath('//p[.//*[contains(text(), "PHONE")]]/text()')
                ).strip()

            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(store.xpath('.//div[contains(@id,"schedule")]/text()'))
                .replace("\n", " ")
                .replace("  ", " ")
                .strip()
            )

            map_link = "".join(
                store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
            ).strip()

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if len(map_link) > 0:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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
