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

    start_url = "https://carefreeboats.com/locations/"
    domain = "carefreeboats.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[strong[a]]")
    for poi_html in all_locations:
        page_url = poi_html.xpath(".//a/@href")[0]
        page_url = urljoin(start_url, page_url)
        location_name = poi_html.xpath(".//a/text()")[0]
        raw_data = poi_html.xpath("text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if len(raw_data) > 2:
            raw_data = [", ".join(raw_data[:2])] + raw_data[2:]
        addr = parse_address_intl(raw_data[0])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        zip_code = addr.postcode
        country_code = ""
        if zip_code and len(zip_code.split()) == 2:
            country_code = "CA"
        else:
            if zip_code:
                country_code = "US"
        if not country_code:
            country_code = addr.country
        state = addr.state
        if state == "Ontario":
            country_code = "CA"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=raw_data[-1],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address=raw_data[0],
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
