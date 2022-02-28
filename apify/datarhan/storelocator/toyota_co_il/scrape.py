import ssl
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.co.il/dealers/dealers"
    domain = "toyota.co.il"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="dealer-details"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath('.//a[@data-gt-action="view-dealer"]/@href')[0]
        page_url = urljoin(start_url, page_url)
        if page_url == "https://www.toyota.co.il/":
            continue
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_address = (
            poi_html.xpath('.//li[@class="address"]/text()')[0].strip().split(" - ")
        )
        city = raw_address[-1]
        street_address = raw_address[0]
        phone = poi_html.xpath('.//li[@class="phone"]/a/text()')[0]
        geo = (
            loc_dom.xpath('//div[@id="map"]/a/@href')[0]
            .split("/")[-1]
            .split("?")[0]
            .split(",")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="IL",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
