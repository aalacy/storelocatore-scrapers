# -*- coding: utf-8 -*-
import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.kendrascott.com/stores/directory"
    domain = "kendrascott.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="btn btn-link highlight-directory"]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="store-name"]/text()')[0]
        if "coming soon" in location_name:
            continue
        raw_data = loc_dom.xpath(
            '//div[@class="store-location-details"]//p[contains(@class, "store-details")]//text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip() and e.strip() != ","]
        phone = loc_dom.xpath(
            '//div[@class="store-contact-details"]/p[@class="store-details text-m"]/text()'
        )[0]
        latitude = re.findall("latitude = (.+?),", loc_response.text)[0]
        longitude = re.findall("longitude = (.+?);", loc_response.text)[0]
        hoo = loc_dom.xpath('//div[@class="store-hours-details"]/time//text()')
        hoo = (
            " ".join([e.strip() for e in hoo if e.strip()])
            .split("Hours")[-1]
            .split("HOURS ")[-1]
        )
        if "PERMANENTLY CLOSED" in hoo:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=raw_data[1],
            state=raw_data[2],
            zip_postal=raw_data[3],
            country_code="",
            store_number=page_url.split("/")[-1],
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
