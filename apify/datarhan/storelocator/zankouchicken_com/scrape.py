# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://zankouchicken.com/locations/"
    domain = "zankouchicken.com"
    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[@class="vc_gitem-link vc-zone-link"]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_data = loc_dom.xpath('//span[@class="addressinfo"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip() and "am -" not in e]
        raw_data = ", ".join(raw_data)
        addr = parse_address_intl(raw_data)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        hoo = loc_dom.xpath(
            '//span[contains(text(), "Hours:")]/following-sibling::span[1]/text()'
        )
        hoo = " ".join(hoo)
        try:
            geo = (
                loc_dom.xpath('//a[contains(@href, "/@")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
        except Exception:
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
                .split("sll=")[-1]
                .split("&")[0]
                .split(",")
            )
        latitude = ""
        longitude = ""
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=raw_data,
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
