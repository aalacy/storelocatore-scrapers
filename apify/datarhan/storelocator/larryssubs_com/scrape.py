from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://larryssubs.com/find"
    domain = "larryssubs.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div[@data-lat]")
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")[0]
        raw_address = poi_html.xpath(".//h5/text()")[:2]
        phone = poi_html.xpath('.//h5[span[contains(text(), "Phone:")]]/text()')
        phone = phone[0].strip() if phone else ""
        store_number = poi_html.xpath('.//h6[contains(text(), "Restaurant #")]/text()')[
            0
        ].split("#")[-1]
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lon")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1].split()[0],
            zip_postal=raw_address[1].split(", ")[-1].split()[-1],
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
