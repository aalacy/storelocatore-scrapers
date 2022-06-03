# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.adecco.com.co/contactanos/"
    domain = "adecco.com.co"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="cnt"]')
    all_locations += dom.xpath('//div[@class="cnt black"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")
        p_class = poi_html.xpath("@class")[0]
        if not location_name and p_class != "cnt black":
            continue
        location_name = location_name[0] if location_name else ""
        street_address = poi_html.xpath(".//a/text()")[0]
        if street_address.endswith("."):
            street_address = street_address[:-1]
        city = poi_html.xpath(".//parent::div/preceding-sibling::h2/text()")
        if not city:
            city = poi_html.xpath(".//preceding-sibling::h2/text()")
        city = city[0]
        if city == "Divisiones Especializadas":
            city = ""
        phone = poi_html.xpath('.//p[contains(text(), "PBX")]/text()')
        phone = (
            phone[0].split(":")[-1].split("/")[0].split("-")[0].replace("PBX", "")
            if phone
            else ""
        )
        geo = poi_html.xpath(".//a/@href")[0].split("/@")[-1].split(",")[:2]
        latitude = ""
        longitude = ""
        if len(geo) > 1:
            latitude = geo[0].split("=")[-1]
            longitude = geo[1].split("&")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="CO",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
