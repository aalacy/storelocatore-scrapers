from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus-canarias.es/concesionarios"
    domain = "lexus-canarias.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@data-aos="fade-up" and h2]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_address = poi_html.xpath(".//h2/following-sibling::p[1]/text()")
        raw_address = [e.strip() for e in raw_address]
        addr = parse_address_intl(", ".join(raw_address))
        street_address = raw_address[0].strip()
        city = addr.city
        if city.endswith("."):
            city = city[:-1]
        if street_address.endswith("."):
            street_address = street_address[:-1]
        phone = (
            poi_html.xpath(".//h2/following-sibling::p[2]/text()")[0]
            .split(":")[-1]
            .strip()
        )
        hoo = poi_html.xpath(".//h2/following-sibling::p[2]/text()")[1:]
        if not hoo:
            hoo = poi_html.xpath(".//h2/following-sibling::p[4]/text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=addr.postcode,
            country_code="ES",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=", ".join(raw_address),
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
