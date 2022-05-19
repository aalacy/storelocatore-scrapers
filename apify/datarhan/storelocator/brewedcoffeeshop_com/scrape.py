# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://brewedcoffeeshop.com/locations/"
    domain = "brewedcoffeeshop.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="elementor-container elementor-column-gap-default" and div[div[div[@data-widget_type="heading.default"]]]]'
    )[1:-1]
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_data = poi_html.xpath(".//p/span/text()")
        raw_address = raw_data[0].split(", ")
        latitude = ""
        longitude = ""
        geo = poi_html.xpath(".//a/@href")[0]
        if "@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hoo = poi_html.xpath(".//text()")
        hoo = ", ".join([e.strip() for e in hoo if "AM" in e])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[-1].split()[0],
            zip_postal=raw_address[-1].split()[-1],
            country_code="",
            store_number="",
            phone=raw_data[1],
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
