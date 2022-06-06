# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://mariosbigpizza.com/"
    domain = "mariosbigpizza.com"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//span[@class="link_to_lacation-page"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath(".//parent::a/@href")[0]
        raw_address = poi_html.xpath(".//text()")[0]
        city = poi_html.xpath(".//parent::a/preceding-sibling::p[1]/text()")[0]
        street_address = raw_address.split(city)[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=street_address,
            street_address=street_address,
            city=city,
            state=raw_address.split(",")[-1].split()[0],
            zip_postal=raw_address.split(",")[-1].split()[1],
            country_code="",
            store_number="",
            phone="",
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
