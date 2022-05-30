from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.ro/contact/dealers/list"
    domain = "lexus.ro"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="dealer-details"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath('.//a[@data-gt-action="view-dealer"]/@href')[0]
        page_url = urljoin(start_url, page_url)
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_address = poi_html.xpath('.//li[@class="address"]/text()')[0]
        zip_code = poi_html.xpath(".//@data-gt-dealerzipcode")[0]
        phone = poi_html.xpath('.//a[@data-gt-action="call-dealer"]/text()')
        phone = phone[0].split(",")[0].split("/")[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address.split(" - ")[0],
            city=raw_address.split(" - ")[1],
            state="",
            zip_postal=zip_code,
            country_code="RO",
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
