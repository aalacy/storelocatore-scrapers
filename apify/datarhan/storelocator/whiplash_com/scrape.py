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

    start_url = "https://whiplash.com/about/locations/"
    domain = "whiplash.com/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//h4/following-sibling::a/@href")
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        all_locations = loc_dom.xpath(
            '//i[@class="fas fa-map-marker text-red my-auto font-size-24 ms-3 ms-sm-0"]/following-sibling::div'
        )
        for poi_html in all_locations:
            raw_data = poi_html.xpath('.//p[@class="text-red mb-0"]/text()')
            raw_data = [e.strip() for e in raw_data]
            raw_address = raw_data[1:]
            if len(raw_data) == 4:
                raw_address = [" ".join(raw_address[1:3])] + raw_address[3:]
            raw_address = " ".join(raw_address)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=raw_data[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="",
                store_number="",
                phone="",
                location_type="",
                latitude="",
                longitude="",
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
