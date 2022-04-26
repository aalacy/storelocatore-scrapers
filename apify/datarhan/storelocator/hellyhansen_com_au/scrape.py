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

    start_url = "https://hellyhansen.com.au/pages/helly-hansen-stores"
    domain = "hellyhansen.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="rte"]/p[descendant::strong]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//strong/text()")[0].replace("\xa0", " ")
        raw_address = poi_html.xpath(".//following-sibling::p[1]//text()")
        raw_address = ", ".join([e for e in raw_address if "Phone" not in e]).split(
            "+"
        )[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = poi_html.xpath(".//following-sibling::p[1]/text()")
        if not phone:
            phone = poi_html.xpath(".//following-sibling::p[1]/span/span/text()")
        phone = phone[0].split(":")[-1].replace("\xa0", " ").strip()
        if not phone.startswith("+"):
            phone = poi_html.xpath(
                './/following-sibling::p[1]//span[contains(text(), "Phone:")]/following-sibling::span[1]/text()'
            )[0]
        if phone.endswith(")"):
            phone += poi_html.xpath(".//following-sibling::p[1]//text()")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="AU",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
