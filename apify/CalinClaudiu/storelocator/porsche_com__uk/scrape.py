# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.porsche.com/all/dealer2/GetLocationsWebService.asmx/GetLocationsInStateSpecialJS?market=uk&siteId=uk&language=none&state=&_locationType=Search.LocationTypes.Dealer&searchMode=proximity&searchKey={}%7C{}&address=&maxproximity=&maxnumtries=&maxresults=&postalcode="
    domain = "porsche.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=10
    )
    for lat, lng in all_codes:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        dom = etree.HTML(response.content)

        all_locations = dom.xpath("//location")
        for poi_html in all_locations:
            store_number = poi_html.xpath(".//id/text()")[0]
            latitude = poi_html.xpath(".//lat/text()")[0]
            longitude = poi_html.xpath(".//lng/text()")[0]
            location_name = poi_html.xpath(".//name/text()")[0]
            zip_code = poi_html.xpath(".//postcode/text()")[0]
            city = poi_html.xpath(".//city/text()")[0]
            street_address = poi_html.xpath(".//street/text()")[0]
            phone = poi_html.xpath(".//phone/text()")
            phone = phone[0] if phone else ""

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.porsche.com/uk/dealersearch/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
                zip_postal=zip_code,
                country_code="UK",
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
