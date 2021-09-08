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

    start_url = "https://www.r-wireless.com/locations/"
    domain = "r-wireless.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="city-name"]/a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = (
            loc_dom.xpath('//script[contains(text(), "page.location")]/text()')[0]
            .split("page.location = ")[-1]
            .strip()[:-1]
        )
        poi = json.loads(poi)

        street_address = poi["Address"].strip()
        if poi["Address2"]:
            street_address += " " + poi["Address2"].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        hoo = loc_dom.xpath(
            '//div[contains(text(), "Hours of Operation")]/following-sibling::ul//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["Name"],
            street_address=street_address,
            city=poi["City"],
            state=poi["ProvinceAbbrev"],
            zip_postal=poi["PostalCode"],
            country_code=poi["CountryCode"],
            store_number=poi["LocationId"],
            phone=poi["Phone"],
            location_type="",
            latitude=poi["Google_Latitude"],
            longitude=poi["Google_Longitude"],
            hours_of_operation=hoo,
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
