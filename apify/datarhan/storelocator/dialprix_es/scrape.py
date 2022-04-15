# -*- coding: utf-8 -*-
import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://dialprix.es/centros/"
    domain = "dialprix.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)

    all_locations = re.findall(
        r"locations.push\((.+?)\);", response.text.replace("\n", "")
    )
    for poi in all_locations:
        poi = json.loads(poi)
        addr = parse_address_intl(poi["address"])
        if len(poi["address"].split(",")) == 5:
            street_address = " ".join(poi["address"].split(",")[:2])
        else:
            street_address = poi["address"].split(",")[0]

        loc_response = session.get(poi["link"])
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[@class="date"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["link"],
            location_name="Supermercado Dialprix",
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="ES",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=poi["hour"],
            raw_address=poi["address"],
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
