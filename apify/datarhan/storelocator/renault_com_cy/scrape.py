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

    start_url = "https://renault.com.cy/home/showroom-garage/"
    domain = "renault.com.cy"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="avia_textblock"]/table/tbody/tr')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//td/strong/text()")[0].replace(":", "")
        if "Showroom" not in location_name:
            continue
        raw_data = poi_html.xpath("./td[1]/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if not raw_data:
            raw_data = poi_html.xpath(".//td/p[1]/text()")
            raw_data = [e.strip() for e in raw_data if e.strip()]
        if not raw_data:
            raw_data = poi_html.xpath("./td[1]/p[2]/text()")
            raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = ", ".join(raw_data)
        addr = parse_address_intl(raw_address)
        hoo = poi_html.xpath("./td[2]/text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="CY",
            store_number="",
            phone="",
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=raw_address,
        )

        yield item

        raw_data_2 = poi_html.xpath(".//td/p[2]/text()")
        if raw_data_2:
            raw_data_2 = [e.strip() for e in raw_data_2 if e.strip()]
            raw_address = ", ".join(raw_data_2)
            addr = parse_address_intl(raw_address)

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=raw_data_2[0],
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="CY",
                store_number="",
                phone="",
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
