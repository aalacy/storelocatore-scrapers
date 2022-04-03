# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://brunosfinefoods.ca/locations"
    domain = "brunosfinefoods.ca"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(5)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//div[div[div[div[div[div[div[iframe]]]]]]]")
    for poi_html in all_locations:
        raw_address = poi_html.xpath(".//following-sibling::div[2]//text()")
        raw_address = [
            e.replace("\xa0", " ").strip()
            for e in raw_address
            if not e.strip().startswith("(") and "(Village" not in e
        ]
        geo = (
            poi_html.xpath(".//iframe/@src")[0]
            .split("center=")[-1]
            .split("&")[0]
            .split(",")
        )
        phone = poi_html.xpath(".//following-sibling::div[3]//text()")[0].replace(
            "Tel.:\xa0", ""
        )
        hoo = poi_html.xpath(".//following-sibling::div[6]//text()")
        if hoo and "Bruno" in hoo[0]:
            hoo = ""
        if not hoo:
            hoo = poi_html.xpath(".//following-sibling::div[5]//text()")
        hoo = hoo[0].replace("Hours:\xa0", "").replace("Hours: ", "")

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name="",
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1],
            zip_postal=raw_address[-1],
            country_code="CA",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
