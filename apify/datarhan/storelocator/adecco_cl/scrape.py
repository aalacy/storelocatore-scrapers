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

    start_url = "https://adecco.cl/contacto/"
    domain = "adecco.cl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[h5 and @class="elementor-widget-container"]')
    for poi_html in all_locations[1:]:
        location_name = poi_html.xpath(".//h5/text()")[0]
        raw_data = poi_html.xpath("text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if not raw_data:
            raw_data = poi_html.xpath(".//p/text()")
            raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = raw_data[0].split("Fono:")[0].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if len(street_address) < 5:
            street_address = raw_address.split(",")[0]
        if len(raw_data) > 1:
            phone = raw_data[1].split(":")[-1]
        else:
            phone = raw_data[0].split("Fono:")[-1]
        phone = phone.split(" – ")[0]
        city = addr.city
        if not city:
            city = location_name
        city = city.replace(".", "")
        if street_address.endswith("."):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=addr.postcode,
            country_code="CL",
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
