# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgFirefox
import time
import ssl
import json
import lxml.html

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "jenningsbet.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    # Your scraper here

    api_url = "https://www.jenningsbet.com/shops/"
    with SgFirefox(block_third_parties=True) as driver:
        driver.get(api_url)
        time.sleep(10)
        html_sel = lxml.html.fromstring(driver.page_source)
        JS_URL = "".join(
            html_sel.xpath('//script[contains(@src,"/shop-locator-app")]/@src')
        ).strip()
        log.info(JS_URL)
        driver.get("https://www.jenningsbet.com" + JS_URL)
        time.sleep(20)
        storeLocations = json.loads(
            driver.page_source.split("JSON.parse('")[1].strip().split("');")[0].strip()
        )["storeLocations"]
        for loc in storeLocations:
            state = loc["areaName"]
            stores = loc["shops"]
            for store in stores:
                locator_domain = website
                page_url = api_url
                location_name = store["name"]

                location_type = "<MISSING>"

                raw_address = store["address"]

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                city = formatted_addr.city
                if city:
                    city = city.replace("Great Clacton", "").strip()

                zip = " ".join(raw_address.split(" ")[-2:]).strip()

                country_code = "GB"

                phone = "<MISSING>"

                hours_of_operation = "<MISSING>"

                store_number = "<MISSING>"

                latitude = store["lat"]
                longitude = store["lon"]

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
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
