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

    start_url = "https://www.toyota.ge/dealers/"
    domain = "toyota.ge"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="title-h5"]/a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath('//p[strong[contains(text(), "მის.:")]]/text()')[
            0
        ].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        location_name = loc_dom.xpath('//div[@class="title-h1"]/text()')[-1].strip()
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="GE",
            store_number="",
            phone=phone,
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
