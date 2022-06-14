# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.briochedoree.fr/restaurants/getStores?q=&editing=true"
    domain = "briochedoree.fr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["result"]:
        page_url = "https://www.briochedoree.fr" + poi["url"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        street_address = poi["address"]["line1"]
        if poi["address"]["line2"]:
            street_address += ", " + poi["address"]["line2"]
        hoo = loc_dom.xpath('//li[@class="StoreDetail-schedulesItem"]/span/text()')
        hoo = " ".join([" ".join(e.split()) for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["displayName"],
            street_address=street_address,
            city=poi["address"]["town"],
            state="",
            zip_postal=poi["address"]["postalCode"],
            country_code="FR",
            store_number=poi["name"],
            phone=poi["address"]["phone"],
            location_type="",
            latitude=poi["geoPoint"]["latitude"],
            longitude=poi["geoPoint"]["longitude"],
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
