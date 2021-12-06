from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.asics.com.br/lojas"
    domain = "asics.com.br"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//ul/div[@data-lat]")
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@class="loja-title"]/text()')[0]
        street_address = poi_html.xpath('.//div[@class="address"]/text()')[0]
        city = poi_html.xpath('.//div[@class="place"]/text()')[0].split(" - ")[0]
        state = poi_html.xpath('.//div[@class="place"]/text()')[0].split(" - ")[-1]
        phone = poi_html.xpath('.//div[@class="telephone"]/text()')[0].split(" - ")[0]
        if "@" in phone:
            phone = ""
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lng")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal="",
            country_code="BR",
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
