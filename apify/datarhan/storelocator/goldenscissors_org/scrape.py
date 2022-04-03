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

    start_url = "https://goldenscissors.org/#"
    domain = "goldenscissors.org"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//ul[@class="list-divider list-border list check"]/li/a/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath("//div/strong/text()")[0]
        raw_data = loc_dom.xpath('//div[@class="entry-title pt-0"]/h4/text()')
        if not raw_data:
            raw_data = loc_dom.xpath("//p/span/strong/text()")
        if not raw_data:
            raw_data = loc_dom.xpath("//div/p/strong/text()")
        if not raw_data:
            raw_data = loc_dom.xpath("//div/h4/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        hoo = loc_dom.xpath('//div[@class="opening-hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()]).split(" Monday")[0]
        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(5)
            driver.switch_to.frame(driver.find_element_by_xpath("//iframe"))
            loc_dom = etree.HTML(driver.page_source)
        raw_address = loc_dom.xpath('//div[@class="address"]/text()')[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        geo = (
            loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="UK",
            store_number="",
            phone=raw_data[-1],
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
