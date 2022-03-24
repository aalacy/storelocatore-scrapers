# -*- coding: utf-8 -*-
import json
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://mominokitokyojapaneselifestyle.com/pages/store-location"
    domain = "mominokitokyojapaneselifestyle.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(25)
        frame = driver.find_element_by_xpath('//iframe[@title="powr map"]')
        driver.switch_to.frame(frame)
        dom = etree.HTML(driver.page_source)
    data = (
        dom.xpath('//script[contains(text(), "window.CONTENT=")]/text()')[0]
        .split("CONTENT=")[1]
        .split("window")[0]
        .strip()[:-1]
    )
    data = json.loads(data)

    for poi in data["locations"]:
        raw_address = poi["address"].split(", ")

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[2].split()[0],
            zip_postal=raw_address[2].split()[-1],
            country_code=raw_address[-1],
            store_number="",
            phone=poi["number"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation="",
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
