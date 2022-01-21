# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://thecodfather.net/en/store-locations"
    domain = "thecodfather.net"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="nearLocations"]/div[@data-store-id]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@class="place"]/p/text()')[0]
        raw_address = poi_html.xpath('.//div[@class="address"]/p/text()')
        hoo = poi_html.xpath('.//div[@class="work-time"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        store_number = poi_html.xpath(".//@data-store")[0]
        latitude = poi_html.xpath(".//@data-lat")[0]
        longitude = poi_html.xpath(".//@data-lng")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0][:-1],
            city=raw_address[1][:-1],
            state=raw_address[-1].split()[0],
            zip_postal=raw_address[-1].split()[-1],
            country_code="",
            store_number=store_number,
            phone="",
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
