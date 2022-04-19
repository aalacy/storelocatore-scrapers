# -*- coding: utf-8 -*-
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.panago.com/false"
    domain = "panago.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//h2/a/@href")
    next_page = dom.xpath('//a[@class="next page-numbers"]/@href')
    while next_page:
        url = urljoin(start_url, next_page[0])
        response = session.get(url, headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath("//h2/a/@href")
        next_page = dom.xpath('//a[@class="next page-numbers"]/@href')

    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[contains(text(), "PostalAddress")]/text()')[0]
        poi = json.loads(poi)
        hoo = []
        for e in poi["openingHoursSpecification"]:
            hoo.append(f'{e["dayOfWeek"]}: {e["opens"]} - {e["closes"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"].replace("&#8211;", "-"),
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["addressCountry"],
            store_number="",
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=poi["geo"]["latitude"],
            longitude=poi["geo"]["longitude"],
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
