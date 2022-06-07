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

    start_url = "https://www.adecco.dk/afdeling/"
    domain = "adecco.dk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="shortcut"]/a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_address = (
            loc_dom.xpath('//p[contains(text(), "Adresse")]/text()')[-1]
            .strip()
            .split(",")
        )
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        geo = (
            loc_dom.xpath("//iframe/@src")[1]
            .split("!2d")[1]
            .split("!2m")[0]
            .split("!3d")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=" ".join(raw_address[1].split()[1:]),
            state="",
            zip_postal=raw_address[1].split()[0],
            country_code="DK",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1],
            longitude=geo[0],
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
