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

    start_url = "https://www.paradiso.com/"
    domain = "paradiso.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[span[contains(text(), "Locations")]]/following-sibling::ul//a/@href'
    )
    for url in list(set(all_locations)):
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_data = loc_dom.xpath(
            '//p[span[contains(text(), "Paradiso Mexican Restaurant")]]/following-sibling::p//text()'
        )
        country_code = loc_dom.xpath("//@country_full")[0]
        latitude = loc_dom.xpath("//@data-lat")
        if not latitude:
            latitude = loc_dom.xpath("//@lat")
        latitude = latitude[0] if latitude else ""
        longitude = loc_dom.xpath("//@data-lng")
        if not longitude:
            longitude = loc_dom.xpath("//@lon")
        longitude = longitude[0] if longitude else ""
        hoo = loc_dom.xpath('//dl[@class="open-hours-data"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=raw_data[1].split(", ")[0],
            street_address=raw_data[0],
            city=raw_data[1].split(", ")[0],
            state=raw_data[1].split(", ")[1].split()[0],
            zip_postal=raw_data[1].split(", ")[1].split()[1],
            country_code=country_code,
            store_number="",
            phone=raw_data[2],
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
