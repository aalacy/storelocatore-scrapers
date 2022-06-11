# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    start_url = "https://iki.lt/iki-parduotuviu-tinklas/"
    domain = "iki.lt"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(5)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="store-list-item"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(
            './/div[@class="store-list-item__header"]/text()'
        )[0]
        raw_address = poi_html.xpath('.//div[@class="col-7 col-sm"]/div[1]/text()')
        raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        geo = poi_html.xpath(".//a/@href")[-1].split("=")[-1].split(",")
        hoo = poi_html.xpath(
            './/div[@class="store-list-item__working-hours"]//span/text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="LT",
            store_number="",
            phone="",
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
            raw_address=raw_address,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
