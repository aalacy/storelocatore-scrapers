# -*- coding: utf-8 -*-
import re
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
    session = SgRequests(verify_ssl=False)
    start_url = "https://www.knightspharmacy.co.uk/find-a-store/"
    domain = "knightspharmacy.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = []
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
        all_locations += dom.xpath('//a[@class="list-link"]/@href')
        next_page = driver.find_element_by_xpath('//a[@class="next-list"]')
        while next_page:
            next_page.click()
            sleep(5)
            dom = etree.HTML(driver.page_source)
            all_locations += dom.xpath('//a[@class="list-link"]/@href')
            try:
                next_page = driver.find_element_by_xpath('//a[@class="next-list"]')
            except Exception:
                next_page = ""

    for page_url in all_locations:
        loc_response = session.get(page_url, headers=hdr)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="hd-typ2"]/text()')[0]
        raw_address = loc_dom.xpath('//div[@class="contact-address"]//text()')
        raw_address = (
            ", ".join([e.strip() for e in raw_address if e.strip()])
            .split("Phone")[0]
            .strip()
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        hoo = loc_dom.xpath('//ul[@class="store-timming"]//text()')
        hoo = " ".join(hoo)
        geo = re.findall(r"LatLng\((.+?)\),", loc_response.text)[0].split(", ")
        city = addr.city
        if not city and street_address.endswith("Brook"):
            street_address = street_address[:-6]
            city = "Brook"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
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
