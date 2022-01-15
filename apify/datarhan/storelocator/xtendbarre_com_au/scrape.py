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

    start_url = "https://www.xtendbarre.com.au/studios/"
    domain = "xtendbarre.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//h4/a/@href")
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        c_soon = loc_dom.xpath('//strong[contains(text(), "Opening soon!")]')
        if c_soon:
            continue

        location_name = loc_dom.xpath("//h1/text()")[0].strip()
        raw_address = loc_dom.xpath('//a[contains(@href, "maps")]/text()')
        raw_address = ", ".join([e.replace("/", ",").strip() for e in raw_address])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        city = addr.city
        if not city:
            city = raw_address.split(", ")[-4]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0].strip()
        latitude = re.findall(r"lat: (.+?),", loc_response.text)[0]
        longitude = re.findall(r"lng: (.+?),", loc_response.text)[0]
        hoo = loc_dom.xpath('//ul[@class="list-hours"]/li//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
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
