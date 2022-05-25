# -*- coding: utf-8 -*-
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://5buds.ca/"
    domain = "5buds.ca"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div/span[@class="address"][1]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//preceding-sibling::p[1]/text()")[0]
        raw_data = poi_html.xpath("text()")
        hoo = poi_html.xpath(".//following-sibling::span/text()")
        hoo = " ".join([e.strip() for e in hoo])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=raw_data[1].split(", ")[0],
            state=raw_data[1].split(", ")[-1],
            zip_postal=raw_data[2],
            country_code="",
            store_number="",
            phone=raw_data[-1],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
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
