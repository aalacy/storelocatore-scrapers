from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://auto.suzuki.gr/dealers"
    domain = "auto.suzuki.gr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="el-collapse-item"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath('.//a[img[@alt="website"]]/@href')
        page_url = page_url[0] if page_url else ""
        location_name = poi_html.xpath(".//h6/text()")[0]
        raw_address = poi_html.xpath(".//h6/following-sibling::span[1]/text()")[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = (
            poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
            .split(",")[0]
            .split("/")[0]
            .strip()
        )
        service = "xhm5mNtBgDwQhMcaIIgEkloiGlCIjydxdtn07BK2cgNsdQnWcJ5XmAYCRc550kGeC7EgpVjXLKFEHMMy0ISRfOVn2n1t+ZUEVksQVdrXqu0inGVqpqvK219mk9rb98Ma7vZok+Ktpt2SOhu3x3kMWRHeej2Ozrkp7PCxlxCfDEGq/PpF387GiDCSgZSIe5d1CaQuxD0HrdUf/PW1E+e8X+UDZjwUghxvdkgmsbF29WGkvs/v7PWPmPXv337h2207O6rp3vl+vXGr9p1njb7AWbHE97+2W2lAAAAAElFTkSuQmCC"
        if not poi_html.xpath(f'.//img[contains(@src, "{service}")]'):
            continue
        hoo = poi_html.xpath(
            './/h6[contains(text(), "Ώρες λειτουργίας έκθεσης")]/following-sibling::p[1]/strong/text()'
        )
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="GR",
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
