from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.is/contact/dealers/list"
    domain = "lexus.is"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    location_name = dom.xpath("//h2/text()")[0]
    raw_address = dom.xpath("//h2/following-sibling::p[1]/text()")[0]
    addr = parse_address_intl(raw_address)
    street_address = addr.street_address_1
    if addr.street_address_2:
        street_address += ", " + addr.street_address_2
    phone = dom.xpath("//h2/following-sibling::p[1]/text()")[1].split(": ")[-1]
    hoo = dom.xpath(
        '//h2[contains(text(), "OPNUNARTÍMAR")]/following-sibling::p/text()'
    )
    hoo = [e.strip() for e in hoo if e.strip()]
    hoo = " ".join(hoo)

    item = SgRecord(
        locator_domain=domain,
        page_url=start_url,
        location_name=location_name,
        street_address=street_address,
        city=addr.city,
        state="",
        zip_postal=addr.postcode,
        country_code="IS",
        store_number="",
        phone=phone,
        location_type="",
        latitude="",
        longitude="",
        hours_of_operation=hoo,
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
