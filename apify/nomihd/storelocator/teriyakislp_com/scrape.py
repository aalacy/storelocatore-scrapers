# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import time

website = "teriyakislp.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://www.teriyakislp.com/"
    with SgChrome() as driver:
        driver.get(search_url)
        time.sleep(10)
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath(
            '//div[@class="row content p-3"]/div[contains(@ng-repeat,"restaurant in")][./div[not(contains(@class,"ng-hide"))]]/div'
        )
        for store in stores:

            page_url = search_url
            locator_domain = website
            location_name = "".join(store.xpath("h1/text()")).strip()
            raw_address = "".join(
                list(
                    filter(
                        str,
                        store.xpath('.//a[./i[@class="fa fa-map-marker"]]//text()'),
                    )
                )
            )

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address:
                street_address = street_address.replace("Ste", "Suite")

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "MX"

            store_number = "<MISSING>"
            phone = "".join(
                store.xpath('.//span[./i[@class="fa fa-phone"]]//text()')
            ).strip()

            location_type = "<MISSING>"
            hours_of_operation = "".join(
                store.xpath('.//span[./i[@class="fa fa-clock-o"]]//text()')
            ).strip()

            map_link = "".join(
                store.xpath('.//a[./i[@class="fa fa-map-marker"]]/@href')
            ).strip()
            latitude, longitude = get_latlng(map_link)

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
