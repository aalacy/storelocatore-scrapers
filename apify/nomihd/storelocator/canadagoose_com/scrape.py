# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
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

website = "canadagoose.com"
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
    search_url = (
        "https://www.canadagoose.com/us/en/find-a-retailer/find-a-retailer.html"
    )

    with SgChrome() as driver:
        driver.get(search_url)
        time.sleep(30)
        search_sel = lxml.html.fromstring(driver.page_source)

        store_list = search_sel.xpath('//div[@class="store"]')
        for store in store_list:

            page_url = store.xpath("./a/@href")[0].strip()
            log.info(page_url)
            driver.get(page_url)
            store_sel = lxml.html.fromstring(driver.page_source)

            locator_domain = website

            street_address = (
                " ".join(
                    store_sel.xpath(
                        '//div[@class="store-info desktop"]//*[@itemprop="streetAddress"]//text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )
            city = (
                " ".join(
                    store_sel.xpath(
                        '//div[@class="store-info desktop"]//*[@itemprop="addressLocality"]//text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
            )
            if city[-1] == ",":
                city = "".join(city[:-1]).strip()

            state = " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="addressRegion"]//text()'
                )
            ).strip()
            zip = " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="postalCode"]//text()'
                )
            ).strip()
            country_code = "CA"

            location_name = "".join(
                store_sel.xpath('//div[@class="store-info desktop"]//h3[last()]/text()')
            ).strip()

            phone = " ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="telephone"]//text()'
                )
            ).strip()

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = "; ".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//*[@itemprop="openingHours"]//text()'
                )
            ).strip()
            map_link = "".join(
                store_sel.xpath(
                    '//div[@class="store-info desktop"]//a[contains(@href,"maps")]/@href'
                )
            )

            latitude, longitude = get_latlng(map_link)

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
