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

    start_url = (
        "https://www.augustahealth.com/patients-visitors/visitor-resources/locations/"
    )
    domain = "augustahealth.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="locations__item"]')
    for poi_html in list(set(all_locations)):
        page_url = poi_html.xpath('.//div[@class="location__foot"]/a/@href')[0]
        location_name = poi_html.xpath('.//h4[@class="location__title"]/a/text()')[0]
        raw_address = poi_html.xpath('.//p[@class="address"]/a/text()')[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[-2] if len(phone) > 1 else phone[0]
        zip_code = addr.postcode
        hoo = poi_html.xpath('.//div[@class="location__body"]//text()')
        hoo = " ".join(
            [e.strip() for e in hoo if e.strip() and "Hours" not in e]
        ).split(zip_code)[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code=addr.country,
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
