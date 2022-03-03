from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://cinnabon.mt/bake-shop-locations-malta/"
    domain = "cinnabon.mt"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class=" full_section_inner clearfix"]/div[@class="wpb_column vc_column_container vc_col-sm-6"]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")[0]
        raw_address = poi_html.xpath('.//a[contains(@href, "maps")]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        phone = poi_html.xpath(
            './/h5[contains(text(), "Phone")]/following-sibling::p[1]/text()'
        )[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state="",
            zip_postal="",
            country_code="MT",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
