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

    start_url = "https://www.rossmann.cz/prodejny"
    domain = "rossmann.cz"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="page-store--store-list"]/a')
    for poi_html in all_locations:
        latitude = poi_html.xpath("@data-latitude")[0]
        longitude = poi_html.xpath("@data-longitude")[0]
        page_url = urljoin(start_url, poi_html.xpath("@href")[0])
        city = poi_html.xpath("@data-ga-city")[0]
        street_address = poi_html.xpath("@data-ga-address")[0].split(", ")[0]
        zip_code = poi_html.xpath("@data-ga-address")[0].split(", ")[-1].split()[0]
        location_name = poi_html.xpath(
            './/div[@class="page-store--store-title"]/text()'
        )[0]
        phone = poi_html.xpath('.//div[@class="page-store--store-phone"]/text()')[
            0
        ].split(":")[-1]
        hoo = poi_html.xpath('.//div[@class="page-store--opening-hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="CZ",
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
