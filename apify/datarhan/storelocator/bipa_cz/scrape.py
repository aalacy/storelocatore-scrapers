# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://bipa.cz/pobocky/"
    domain = "bipa.cz"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    raw_data = dom.xpath("//figure/blockquote/p[3]/text()")
    raw_data = "; ".join(raw_data)
    raw_data = raw_data.split(" Neděle: Zavřeno")

    for poi in raw_data:
        if not poi.strip():
            continue

        poi = poi.split("; ")
        poi = [e.strip() for e in poi if e.strip()]
        hoo = " ".join(poi[3:]) + " Neděle: Zavřeno"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi[0],
            street_address=poi[1],
            city=" ".join(poi[2].split()[1:]),
            state="",
            zip_postal=poi[2].split()[0],
            country_code="CZ",
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
