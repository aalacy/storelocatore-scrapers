# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://wackys.com/locations/locations.xml"
    domain = "wackys.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.XML(response.content)
    all_locations = dom.xpath("//marker")
    for poi_html in all_locations:
        location_name = poi_html.xpath("@name")[0]
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]
        location_type = poi_html.xpath("@category")[0]
        street_address = poi_html.xpath("@address")[0]
        st_address_2 = poi_html.xpath("@address2")
        if st_address_2:
            street_address += " " + st_address_2[0]
        city = poi_html.xpath("@city")[0]
        state = poi_html.xpath("@state")[0]
        zip_code = poi_html.xpath("@postal")[0]
        country_code = poi_html.xpath("@country")[0]
        phone = poi_html.xpath("@phone")[0]
        hoo = poi_html.xpath("@hours1")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://wackys.com/locations/",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type=location_type,
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
