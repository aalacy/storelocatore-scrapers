from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "thedaileymethod.com"
    start_url = "https://thedaileymethod.com/wp-content/themes/dailey-method/locations.xml?origLat=56.130366&origLng=-106.346771&origAddress=canada"

    response = session.get(start_url)
    dom = etree.HTML(response.content)

    all_locations = dom.xpath("//marker")
    for poi_html in all_locations:
        page_url = poi_html.xpath("@web")[0]
        location_name = poi_html.xpath("@name")[0]
        street_address = poi_html.xpath("@address")[0]
        city = poi_html.xpath("@city")[0]
        state = poi_html.xpath("@state")[0]
        zip_code = poi_html.xpath("@postal")[0]
        phone = poi_html.xpath("@phone")[0]
        country = poi_html.xpath("@country")[0]
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country,
            store_number="",
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
