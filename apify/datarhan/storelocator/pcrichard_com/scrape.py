import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    domain = "pcrichard.com"
    start_url = "https://www.pcrichard.com/store-locator/"
    hdr = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    }

    response = session.get(start_url, headers=hdr, verify=False)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//div[@class="storelocator-state-links"]//a/@href')

    for url in all_urls:
        store_url = urljoin(start_url, url)
        store_response = session.get(store_url, headers=hdr, verify=False)
        loc_dom = etree.HTML(store_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')[0]
        poi = json.loads(poi)
        geo = loc_dom.xpath("//@data-locations")[0]
        geo = json.loads(geo)[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["name"],
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=poi["address"]["postalCode"],
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=geo["latitude"],
            longitude=geo["longitude"],
            hours_of_operation=" ".join(poi["openingHours"]),
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
