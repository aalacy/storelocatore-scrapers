# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgselenium import SgChrome
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

website = "frv21.com.br"
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

    search_url = "https://frv21.com.br/stores"

    with SgChrome() as driver:
        driver.get(search_url)
        stores_sel = lxml.html.fromstring(driver.page_source)
        stores = stores_sel.xpath(
            '//ul[@class="stores__list"]/li[@class="stores__item"]'
        )
        for store in stores:

            page_url = search_url

            store_info = store.xpath('span[@class="stores__item--address"]/text()')

            location_name = store_info[0]
            location_type = "<MISSING>"
            raw_address = "<MISSING>"

            locator_domain = website

            street_address = store_info[1]
            city = "".join(
                store.xpath('h5[@class="stores__item--city"]/text()')
            ).strip()

            state = "".join(
                store.xpath('h4[contains(@class,"stores__item--state")]/text()')
            ).strip()
            zip = "<MISSING>"

            country_code = "BR"

            store_number = "<MISSING>"
            phone = "".join(
                store.xpath('.//p[@class="stores__item--phone"]/text()')
            ).strip()

            hours_of_operation = "<MISSING>"

            map_link = "".join(
                store.xpath('.//a[@class="stores__item--maps"]/@href')
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
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
