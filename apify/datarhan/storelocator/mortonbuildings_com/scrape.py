# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)
    domain = "mortonbuildings.com"
    start_url = "https://mortonbuildings.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = json.loads(dom.xpath("//@data-dna")[0])
    all_locations = [e for e in data if e["type"] == "markers"]
    for poi in all_locations:
        poi_html = etree.HTML(poi["options"]["infoWindowOptions"]["content"])
        zip_code = poi_html.xpath("//@data-zip")[0]
        city = poi_html.xpath("//@data-city-state")[0].split(", ")[0]
        state = poi_html.xpath("//@data-city-state")[0].split(", ")[-1]
        page_url = poi_html.xpath("//a/@href")[0]
        location_name = poi_html.xpath("//a/text()")[0].strip()
        phone = poi_html.xpath('//a[@class="phone-link"]/text()')[0].strip()
        street_address = poi_html.xpath("//address/text()")[0].strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=poi["locations"][0]["lat"],
            longitude=poi["locations"][0]["lng"],
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
