# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.santander.com.pe/footer/canales-de-atencion.html"
    domain = "santander.com.pe"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(
        "https://www.santander.com.pe/public/assets/files/json/BranchOffice.json",
        headers=hdr,
    ).json()
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    for poi in all_locations:
        raw_address = poi["OfficeAddress"].replace("&#243;", "ó").split(" - ")
        hoo = dom.xpath('//p[contains(text(), "Horario")]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=raw_address[0],
            street_address=raw_address[1],
            city=raw_address[-1].split(", ")[0],
            state=raw_address[-1].split(", ")[-1],
            zip_postal="",
            country_code="PE",
            store_number="",
            phone="",
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
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
