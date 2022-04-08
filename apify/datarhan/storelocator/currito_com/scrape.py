# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.currito.com/locations/"
    domain = "currito.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//h3[@itemprop="name"]/text()')[0]
        street_address = poi_html.xpath('.//span[@itemprop="streetAddress"]/text()')[0]
        city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')[0]
        state = poi_html.xpath('.//span[@itemprop="addressRegion"]/text()')[0]
        zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')[0]
        hoo = poi_html.xpath('.//span[@class="hours"]//p/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        if "Express" in hoo:
            hoo = ""
        latitude = ""
        longitude = ""
        geo = poi_html.xpath('.//a[contains(text(), "Directions")]/@href')
        if geo and "@" in geo[0]:
            geo = geo[0].split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        phone = poi_html.xpath('.//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
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
