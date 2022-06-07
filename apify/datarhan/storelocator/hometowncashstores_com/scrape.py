# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://hometowncashstores.com/locations/_includes/sqlsearch.php?lat=40.75368539999999&lng=-73.9991637&radius=60000"
    domain = "hometowncashstores.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.XML(response.text)

    all_locations = dom.xpath("//marker")
    for poi_html in all_locations:
        location_name = poi_html.xpath("@BizName")[0]
        street_address = poi_html.xpath("@BizStreet")[0]
        street_address_2 = poi_html.xpath("@BizStreet2")
        if street_address_2 and street_address_2[0].strip():
            street_address += ", " + street_address_2[0].strip()
        city = poi_html.xpath("@BizCity")[0]
        state = poi_html.xpath("@BizState")[0]
        zip_code = poi_html.xpath("@BizZip")[0]
        phone = poi_html.xpath("@BizPhone")[0]
        store_number = poi_html.xpath("@StoreNumber")[0]
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://hometowncashstores.com/locations.php",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
