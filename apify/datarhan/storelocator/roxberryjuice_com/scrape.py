# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.roxberryjuice.com/locations/"
    domain = "roxberryjuice.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="dmRespColsWrapper"]/div[@class="dmRespCol small-12 large-3 medium-3"]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/span/text()")
        if not location_name:
            continue
        raw_address = poi_html.xpath(".//div/p/span/text()")
        if not raw_address:
            continue
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        city = addr.city
        if not city and "orem" in street_address.lower():
            city = "Orem"
            street_address = street_address.replace("Orem", "").strip()
        state = addr.state
        if not state and street_address.lower().endswith("ut"):
            state = "UT"
            street_address = street_address[:-2]
        phone = poi_html.xpath(".//a/text()")
        if not phone:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name[0],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone[0],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
