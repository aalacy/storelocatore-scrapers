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

    start_url = "https://www.toyota.is/um-toyota/soluadilar/opnunartimar"
    domain = "toyota.is"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="text" and descendant::h3[a]]')
    for poi_html in all_locations:
        url = poi_html.xpath(".//h3/a/@href")[0]
        page_url = urljoin(start_url, url)
        location_name = poi_html.xpath(".//h3/a/text()")[0]
        raw_data = poi_html.xpath(".//h3/following-sibling::p[1]/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = raw_data[0]
        addr = parse_address_intl(raw_address)
        city = addr.city
        street_address = raw_address.split(city)[0].split(",")[0].strip()
        phone = [e.split(":")[-1].strip() for e in raw_data if "mi:" in e][0]
        hoo = [e for e in raw_data if "- 1" in e]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
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
