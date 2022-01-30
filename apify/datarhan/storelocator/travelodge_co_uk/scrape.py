import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "travelodge.co.uk"
    start_url = "https://www.travelodge.co.uk/search_and_book/a-to-z/"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//a[@class="espotLink"]/@href')

    for url in all_cities:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(@href, "/hotels/")]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)
        all_locations += dom.xpath('//a[span[contains(text(), "View hotel")]]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)
        all_locations += dom.xpath('//a[span[contains(text(), "View hotel")]]/@href')

        location_name = loc_dom.xpath('//h1[@property="schema:name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@property="schema:address"]/text()')
        raw_address = [
            " ".join([e.strip() for e in elem.strip().split()])
            for elem in raw_address
            if elem.strip()
        ]
        if not raw_address:
            continue
        raw_address = (
            " ".join(raw_address)
            .replace("Postcode", "")
            .replace("Sat nav postcode:", "")
            .replace("Tel:", "")
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = loc_dom.xpath('//a[@class="telephone"]/text()')[0]
        latitude = re.findall(r"hotelLat: '(.+?)',", loc_response.text)[0]
        longitude = re.findall(r"hotelLng: '(.+?)',", loc_response.text)[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=store_url.split("/")[-2],
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
            raw_address=raw_address,
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
