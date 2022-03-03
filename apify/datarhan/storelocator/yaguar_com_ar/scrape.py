# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://www.yaguar.com.ar/category/sucursales/"
    domain = "yaguar.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//h1[contains(text(), "Más sucursales")]/following-sibling::article//h2/a/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="entry-title"]/text()')[0].replace(
            ".", ""
        )
        raw_address = loc_dom.xpath(
            '//i[@class="fas fa-map-marker"]/following-sibling::div[1]/text()'
        )[0].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        city = addr.city
        if city and city.endswith("."):
            city = city[:-1]
        if street_address.endswith("."):
            street_address = street_address[:-1]
        phone = (
            loc_dom.xpath(
                '//i[@class="fas fa-phone"]/following-sibling::div[1]/text()'
            )[0]
            .split("/")[0]
            .strip()
        )
        phone = (
            phone.replace("rotativas", "")
            .split(" (")[0]
            .split("- 15")[0]
            .split("-  15")[0]
            .strip()
        )
        if phone.endswith("-"):
            phone = phone[:-1]
        hoo = loc_dom.xpath(
            '//i[@class="fas fa-clock"]/following-sibling::div[1]/text()'
        )[0]
        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(15)
            loc_dom = etree.HTML(driver.page_source)
        geo = (
            loc_dom.xpath("//iframe/@src")[-1].split("q=")[-1].split("&")[0].split(",")
        )
        latitude = ""
        longitude = ""
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
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
