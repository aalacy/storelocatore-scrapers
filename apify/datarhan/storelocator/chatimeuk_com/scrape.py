# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.chatimeuk.com/locations"
    domain = "chatimeuk.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//p[@class="font_8" and descendant::a[contains(@href, "goo.gl")]]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//a//text()")[0]
        street_address = poi_html.xpath(".//following-sibling::p[1]//text()")[0]
        city = poi_html.xpath(".//following-sibling::p[2]//text()")[0]
        zip_code = poi_html.xpath(".//following-sibling::p[3]//text()")[0]
        if (
            "Unit" in street_address
            or "11 Harbour Island" in street_address
            or "170 High Street" in street_address
            or "53 Chapel" in street_address
            or "Island Site" in street_address
            or "2 The Square" in street_address
        ):
            street_address += ", " + city
            city = poi_html.xpath(".//following-sibling::p[3]//text()")[0]
            zip_code = poi_html.xpath(".//following-sibling::p[4]//text()")[0]
        if "Kiosk B" in street_address:
            street_address += ", " + city
            street_address += (
                ", " + poi_html.xpath(".//following-sibling::p[3]//text()")[0]
            )
            city = poi_html.xpath(".//following-sibling::p[4]//text()")[0]
            zip_code = poi_html.xpath(".//following-sibling::p[5]//text()")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address.replace(", ,", ","),
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone="",
            location_type="",
            latitude="",
            longitude="",
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
