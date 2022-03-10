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

    start_url = "https://www.mindspace.me/#"
    domain = "mindspace.me"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_cities = dom.xpath('//a[@class="location-list-link"]/@href')
    for url in all_cities:
        response = session.get(url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//a[contains(text(), "More details")]/@href')
        for page_url in all_locations:
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            raw_address = loc_dom.xpath('//p[@class="location-address"]/text()')[0]
            addr = parse_address_intl(raw_address)
            location_name = loc_dom.xpath('//h1[@class="h1 location-title"]/text()')[0]
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            phone = loc_dom.xpath('//a[@class="phone-link"]/text()')[-1]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
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
