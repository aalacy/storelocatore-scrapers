from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://popeyesmexico.mx/sucursales/"
    domain = "popeyesmexico.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="my-grid-layout"]/div[@class="listing-item"]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//span[@class="title"]/text()')[0]
        raw_adr = (
            poi_html.xpath('.//span[@class="excerpt"]/text()')[0]
            .split("Pick & Go:")[0]
            .strip()
        )
        raw_adr = " ".join(raw_adr.split()).replace(" CDMX,", "")
        addr = parse_address_intl(raw_adr)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = poi_html.xpath('.//span[@class="excerpt"]/text()')[0]
        phone = phone.split("Pick & Go:")[-1].strip() if "Pick & Go" in phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="MX",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address=raw_adr,
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
