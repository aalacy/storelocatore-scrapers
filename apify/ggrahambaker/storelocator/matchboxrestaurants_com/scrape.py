# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.matchboxrestaurants.com/home-locations"
    domain = "matchboxrestaurants.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[@href="/menu-and-locations"]/following-sibling::span/a/@href'
    )
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        c_soon = loc_dom.xpath('//em[contains(text(), "coming soon")]')
        if c_soon:
            continue

        raw_data = loc_dom.xpath(
            '//p[strong[contains(text(), "LOCATION")]]/following-sibling::p/text()'
        )[:2]
        if "suite" in raw_data[1]:
            raw_data = loc_dom.xpath(
                '//p[strong[contains(text(), "LOCATION")]]/following-sibling::p/text()'
            )[:3]
            raw_data = [", ".join(raw_data[:2])] + raw_data[2:]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        if not phone:
            phone = loc_dom.xpath('//p[contains(text(), "call")]/text()')
        phone = phone[0].replace("call ", "") if phone else ""
        location_name = loc_dom.xpath("//h1/text()")[0]
        hoo = loc_dom.xpath(
            '//p[strong[contains(text(), "HOURS")]]/following-sibling::p/text()'
        )
        hoo = (
            " ".join(" ".join(hoo).split())
            .split("dine")[0]
            .replace("\xa0", "")
            .split("social hour")[0]
            .split("From")[0]
            .split("Follow")[0]
        )
        latitude = ""
        longitude = ""
        geo = (
            loc_dom.xpath('//a[contains(text(), "get directions")]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        if len(geo) > 1:
            latitude = geo[0]
            longitude = geo[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=raw_data[1].split(", ")[0],
            state=raw_data[1].split(", ")[-1].split()[0],
            zip_postal=raw_data[1].split(", ")[-1].split()[1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
