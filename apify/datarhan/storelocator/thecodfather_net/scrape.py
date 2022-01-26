# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://thecodfather.net/en/store-locations"
    domain = "thecodfather.net"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(
        "https://thecodfather.order-now.menu/order#/collection", headers=hdr
    )
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "FastFoodRestaurant")]/text()')[
        0
    ].strip()

    all_locations = json.loads(data)
    for poi in all_locations:
        hoo = []
        for e in poi["openingHoursSpecification"]:
            day = e["dayOfWeek"].split("/")[-1]
            opens = e["opens"][:-3]
            closes = e["closes"][:-3]
            hoo.append(f"{day}: {opens} - {closes}")
        hoo = " ".join(hoo)
        state = ""
        if len(poi["address"]["postalCode"].split()) == 2:
            state = poi["address"]["postalCode"].split()[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=poi["name"],
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=state,
            zip_postal=poi["address"]["postalCode"].split()[-1],
            country_code=poi["address"]["addressCountry"],
            store_number="",
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=poi["geo"]["latitude"],
            longitude=poi["geo"]["longitude"],
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
