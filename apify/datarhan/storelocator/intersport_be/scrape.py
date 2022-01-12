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

    start_url = "https://intersport.be/nl-be/winkels/"
    domain = "intersport.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    data = (
        dom.xpath('//script[contains(text(), "locations")]/text()')[0]
        .split("locations =")[-1]
        .strip()
    )
    data = json.loads(data)
    for store_number, poi in data.items():
        poi_html = etree.HTML(poi["html"])
        raw_address = poi_html.xpath('//div[@class="address"]/text()')
        raw_address = [e.strip() for e in raw_address]
        phone = poi_html.xpath('//a[@class="phone station-phone"]/text()')[0]
        loc_response = session.get(poi["url"])
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[h2[contains(text(), "Openingsuren")]]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()][1:])

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["url"],
            location_name=poi["name"],
            street_address=raw_address[0],
            city=raw_address[1].split()[-1],
            state="",
            zip_postal=raw_address[1].split()[0],
            country_code=raw_address[-1],
            store_number=store_number.replace("location", ""),
            phone=phone,
            location_type="",
            latitude=poi["coords"]["lat"],
            longitude=poi["coords"]["lng"],
            hours_of_operation="",
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
