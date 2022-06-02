# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.rossmann.com.tr/storelocator/view/locations/city/0"
    domain = "rossmann.com.tr"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//marker")
    for poi_html in all_locations:
        store_number = poi_html.xpath("@storeid")[0]
        location_name = poi_html.xpath("@name")[0]
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]
        street_address = poi_html.xpath("@address")[0]
        city = poi_html.xpath("@city")[0]
        state = poi_html.xpath("@state")[0]
        phone = poi_html.xpath("@phone")[0]
        hoo = poi_html.xpath("@openinghours")
        hoo = hoo[0] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.rossmann.com.tr/storelocator/view/stores/city/0",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal="",
            country_code="TR",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
