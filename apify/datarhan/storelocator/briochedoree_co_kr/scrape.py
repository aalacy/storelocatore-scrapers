# -*- coding: utf-8 -*-
import os
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl

proxy = "http://groups-RESIDENTIAL,country-kr:{}@proxy.apify.com:8000/"
os.environ["HTTPS_PROXY"] = proxy


def fetch_data():
    start_url = "http://briochedoree.co.kr/store/"
    domain = "briochedoree.co.kr"

    with SgChrome as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath(
        '//div[@class="hc-p2 hc-border hc-rounded hc-mb1 hc-border-green lpr-location lpr-location-featured"]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(
            './/div[@class="hc-bold lpr-location-name"]/text()'
        )[0]
        raw_address = poi_html.xpath(
            './/div[@class="hc-italic lpr-location-address"]/text()'
        )[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath('.//div[@class="lpr-location-phone"]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="KR",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
