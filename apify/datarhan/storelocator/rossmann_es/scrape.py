# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.rossmann.es/nuestras-tiendas/"
    domain = "rossmann.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//p[span[@style="color: #d12230;" and strong]]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//strong/text()")[0]
        raw_address = poi_html.xpath("text()")
        if len(raw_address) > 3:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        if "–" in raw_address[1]:
            city = raw_address[1].split("–")[-1]
            zip_code = raw_address[1].split("–")[0]
        else:
            city = raw_address[1].split()[-1]
            zip_code = raw_address[1].split()[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="ES",
            store_number="",
            phone="",
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=" ".join(raw_address[2:]),
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
