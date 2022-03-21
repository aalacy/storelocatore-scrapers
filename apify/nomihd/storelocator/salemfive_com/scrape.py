# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "salemfive.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.salemfive.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//ul[@class="list-unstyled list-locations-links"]//li/a/@href'
    )
    for store_url in stores:
        if "#locations" in store_url:
            continue

        page_url = "https://www.salemfive.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(store_sel.xpath("//div/h1/text()")).strip()
        location_type = "<MISSING>"
        locator_domain = website
        phone = "".join(
            store_sel.xpath('//div[@class="hidden-xs locationPagePhone"]/text()')
        ).strip()

        raw_address = "".join(
            store_sel.xpath('//div[@id="locationPageAddress"]/text()')
        ).strip()

        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zipp = formatted_addr.postcode

        days = store_sel.xpath('//dl[@id="StaticHours"]/dt/text()')
        time = store_sel.xpath('//dl[@id="StaticHours"]/dd/text()')
        hours_list = []
        for hour in zip(days, time):
            hours_list.append(hour[0] + ":" + hour[1])

        hours_of_operation = "; ".join(hours_list).strip()

        country_code = "US"
        store_number = "<MISSING>"

        latitude = "".join(
            store_sel.xpath('//input[@id="locationPageLat"]/@value')
        ).strip()
        longitude = "".join(
            store_sel.xpath('//input[@id="locationPageLng"]/@value')
        ).strip()

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zipp,
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
