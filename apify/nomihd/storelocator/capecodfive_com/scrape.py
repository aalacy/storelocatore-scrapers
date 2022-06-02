# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "capecodfive.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.capecodfive.com/personal/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="item-list"]//li')

    lat_lng_list = stores_sel.xpath('//span[@typeof="GeoCoordinates"]')
    for index, store in enumerate(stores, 0):
        page_url = (
            "https://www.capecodfive.com"
            + "".join(
                store.xpath(
                    './/div[@class="views-field views-field-title"]/span/a/@href'
                )
            ).strip()
        )
        locator_domain = website
        location_name = "".join(
            store.xpath('.//div[@class="views-field views-field-title"]/span/a/text()')
        ).strip()
        if location_name == "":
            location_name = "<MISSING>"

        street_address = (
            "".join(
                store.xpath(
                    './/p[@class="address"]/span[@class="address-line1"]/text()'
                )
            )
            .strip()
            .replace("(also accessible from Tupper Rd)", "")
            .strip()
        )
        city = "".join(
            store.xpath('.//p[@class="address"]/span[@class="locality"]/text()')
        ).strip()
        state = "".join(
            store.xpath(
                './/p[@class="address"]/span[@class="administrative-area"]/text()'
            )
        ).strip()
        zip = "".join(
            store.xpath('.//p[@class="address"]/span[@class="postal-code"]/text()')
        ).strip()
        country_code = "".join(
            store.xpath('.//p[@class="address"]/span[@class="country"]/text()')
        ).strip()

        store_number = "<MISSING>"
        phone = "".join(store.xpath('.//a[contains(@href,"tel:")]/text()')).strip()

        location_type = "<MISSING>"

        latitude = "".join(
            lat_lng_list[index].xpath("meta[@property='latitude']/@content")
        ).strip()
        longitude = "".join(
            lat_lng_list[index].xpath("meta[@property='longitude']/@content")
        ).strip()

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        hours = store_sel.xpath('//span[@class="office-hours__item"]')

        hours_list = []
        for hour in hours:
            day = "".join(
                hour.xpath('span[@class="office-hours__item-label"]/text()')
            ).strip()
            time = "".join(
                hour.xpath('span[@class="office-hours__item-slots"]/text()')
            ).strip()
            hours_list.append(day + time)

        hours_of_operation = "; ".join(hours_list).strip()

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
