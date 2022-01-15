# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.pepes.co.uk/our-stores"
    domain = "pepes.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@id="StoreLocations"]/div[@class="birming-colmn-one"]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_address = poi_html.xpath('.//div[@class="new-con-oak"]/text()')[0].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = (
            poi_html.xpath('.//div[@class="new-con-oak"]/text()')[1]
            .split("Tel:")[-1]
            .strip()
        )
        hoo = poi_html.xpath(
            './/p[strong[contains(text(), "OPENING TIMES")]]/following-sibling::p/text()'
        )
        if hoo:
            hoo = " ".join(hoo[0].split())
        else:
            hoo = ""
        latitude = poi_html.xpath(".//@lat")[0]
        longitude = poi_html.xpath(".//@lng")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=raw_address,
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
