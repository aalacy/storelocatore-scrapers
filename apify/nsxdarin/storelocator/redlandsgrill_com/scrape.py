# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://redlandsgrill.com/locations/"
    domain = "redlandsgrill.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="restaurantCard"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h4/text()")[0]
        raw_address = poi_html.xpath(".//address/text()")
        if len(raw_address) > 2:
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
        geo = poi_html.xpath('.//a[contains(@href, "ultipro.com")]/@href')
        if geo:
            geo = geo[0].split("=")[-2].split("%7C")[0].split("%2C")
        if not geo:
            geo = poi_html.xpath('.//a[contains(@href, "/@")]/@href')
            if geo:
                geo = geo[0].split("@")[-1].split(",")[:2][::-1]
        if not geo:
            geo = poi_html.xpath('.//a[contains(@href, "maps")]/@href')
            if geo:
                if "&ll=" in geo[0]:
                    geo = geo[0].split("&ll=")[-1].split("&")[0].split(",")[::-1]
                else:
                    geo = geo[0].split("sll=")[-1].split("&")[0].split(",")[::-1]
            else:
                geo = ["", ""]
        if len(geo) == 1:
            geo = ["", ""]
        hoo = poi_html.xpath('.//div[@class="details hours"]/p/text()')
        hoo = [e.strip() for e in hoo if e.strip() and "Open" not in e]
        hoo = (
            " ".join(hoo).split("phone. ")[-1].split("Available ")[-1].split("Take")[0]
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0].split("Fritz Farm,")[-1],
            city=raw_address[1].split(", ")[0],
            state=" ".join(raw_address[1].split(", ")[1].split()[:-1]),
            zip_postal=raw_address[1].split(", ")[1].split()[-1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1],
            longitude=geo[0],
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
