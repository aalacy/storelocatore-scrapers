# -*- coding: utf-8 -*-
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.calgarycoop.com/stores"
    domain = "calgarycoop.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    data = (
        dom.xpath('//script[contains(text(), "mapData")]/text()')[0]
        .split("mapData =")[-1]
        .strip()[:-1]
    )
    all_locations = json.loads(data)
    for poi in all_locations:
        page_url = urljoin(start_url, poi["link"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath('//p[contains(text(), "Phone")]/span/text()')[0]
        hoo = loc_dom.xpath(
            '//h5[contains(text(), "Food Centre")]/following-sibling::p/span[@class="hours"]/text()'
        )
        hoo = hoo[0] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city_prov"].split(", ")[0],
            state=poi["city_prov"].split(", ")[-1],
            zip_postal=poi["postal"],
            country_code="",
            store_number=poi["id"],
            phone=phone,
            location_type=poi["services"],
            latitude=poi["lat"],
            longitude=poi["lon"],
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
