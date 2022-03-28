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

    start_url = "https://serendipitylabs.com/us/"
    domain = "serendipitylabs.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="row location link-stretched"]//a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        data = loc_dom.xpath('//script[@class="yoast-schema-graph"]/text()')[0]
        data = json.loads(data)
        poi_adr = [e for e in data["@graph"] if e["@type"] == "PostalAddress"][0]
        poi = [e for e in data["@graph"] if "Place" in e["@type"]][0]
        hoo = []
        for e in poi["openingHoursSpecification"]:
            for day in e["dayOfWeek"]:
                hoo.append(f'{day}: {e["opens"]} - {e["closes"]}')
        hoo = ", ".join(hoo).replace("00:00 - 00:00", "closed")

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"].replace("&#8211;", "-"),
            street_address=poi_adr["streetAddress"],
            city=poi_adr["addressLocality"],
            state=poi_adr["addressRegion"],
            zip_postal=poi_adr["postalCode"],
            country_code=poi_adr["addressCountry"],
            store_number="",
            phone=poi["telephone"][0],
            location_type="",
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
