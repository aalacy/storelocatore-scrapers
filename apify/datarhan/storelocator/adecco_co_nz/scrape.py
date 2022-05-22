# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from time import sleep
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://www.adecco.co.nz/our-locations/"
    domain = "adecco.co.nz"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="branch-locator__results"]//a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="contact-meta-info"]/h6/text()')[
            0
        ].strip()
        phone = (
            loc_dom.xpath(
                '//small[contains(text(), "Phone number")]/following-sibling::p[1]/text()'
            )[0]
            .split(":")[-1]
            .strip()
        )
        latitude = ""
        longitude = ""
        geo = loc_dom.xpath('//iframe[contains(@src, "maps")]/@src')
        if geo:
            geo = geo[0].split("!2d")[-1].split("!2m")[0].split("!3d")
            latitude = geo[0]
            longitude = geo[1]
        hoo = loc_dom.xpath('//div[@class="branch-locator__opening"]//li/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(10)
            try:
                driver.switch_to.frame(
                    driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
                )
                loc_dom = etree.HTML(driver.page_source)
            except Exception:
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath('//div[@class="address"]/text()')
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//small[contains(text(), "Address")]/following-sibling::div/text()'
            )
            raw_address = [e.strip() for e in raw_address if e.strip()]
            if not raw_address:
                raw_address = loc_dom.xpath(
                    '//small[contains(text(), "Address")]/following-sibling::p[1]/text()'
                )
            raw_address = [e.strip() for e in raw_address if e.strip()]
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="NZ",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
