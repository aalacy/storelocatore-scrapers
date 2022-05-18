# -*- coding: utf-8 -*-
import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://texaco.nl/tankstations/"
    domain = "texaco.nl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    data = dom.xpath('//script[contains(text(), "var marker")]/text()')[0]
    all_locations = re.findall('href="(.+?)" class="button', data)
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_data = loc_dom.xpath('//p[a[contains(@href, "tel")]]/text()')
        raw_address = " ".join(raw_data)
        addr = parse_address_intl(raw_address)
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        if phone and len(phone) < 4:
            phone = ""
        hoo = loc_dom.xpath('//ul[@class="openingHours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        country_code = addr.country
        if country_code and len(country_code) > 2:
            country_code = ""
        if " NL " in raw_address:
            country_code = "NL"
        city = addr.city
        if city and len(city) == 2:
            city = ""
        if city:
            city = city.split("/")[0]
        zip_code = addr.postcode
        street_address = raw_data[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
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
