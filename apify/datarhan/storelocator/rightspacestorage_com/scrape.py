import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://rightspacestorage.com/self-storage-locations/"
    domain = "rightspacestorage.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//ul[@class="listing-holder"]/li/a/@href')
    for url in all_cities:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//a[contains(text(), "View All Units")]/@href')

        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            poi = loc_dom.xpath('//script[contains(text(), "addressRegion")]/text()')[
                -1
            ]
            poi = json.loads(poi)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["description"],
                street_address=poi["address"]["streetAddress"].replace("&#039;", "'"),
                city=poi["address"]["addressLocality"],
                state=poi["address"]["addressRegion"],
                zip_postal=poi["address"]["postalCode"],
                country_code="",
                store_number="",
                phone=poi["telephone"],
                location_type=poi["@type"],
                latitude=poi["geo"]["longitude"],
                longitude=poi["geo"]["latitude"],
                hours_of_operation=poi["openingHours"],
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
