from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    scraped_items = []
    start_url = "https://bolichesamf.com/sucursales/"
    domain = "bolichesamf.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[div[section[div[div[div[div[div[h2[contains(text(), "bol ")]]]]]]]]]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        if location_name in scraped_items:
            continue
        scraped_items.append(location_name)
        raw_address = poi_html.xpath('.//span[contains(text(), "N. L.")]/text()')
        state = "N. L."
        if not raw_address:
            raw_address = poi_html.xpath('.//span[contains(text(), "CDMX")]/text()')
            state = "CDMX"
        raw_address = raw_address[0].strip()
        if raw_address.endswith("."):
            raw_address = raw_address[:-1]
        addr = parse_address_intl(raw_address)
        city = addr.city
        if city and city.lower() == "cdmx":
            city = "Mexico"
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        if street_address == "N. L":
            street_address = ""
        if "Monterrey N. L" in street_address:
            street_address = street_address.replace(" Monterrey N. L", "")
            city = "Monterrey"
        phone = poi_html.xpath(
            './/p[descendant::span[contains(text(), "Tels:")]]/following-sibling::p/span/span/text()'
        )
        if not phone:
            phone = poi_html.xpath(
                './/p[descendant::span[contains(text(), "Tels:")]]/following-sibling::p//span/text()'
            )[:-1]
        phone = [e.replace("\xa0", "") for e in phone if e.strip()]
        phone = " ".join(phone).replace("Tels: ", "")
        geo = (
            poi_html.xpath('.//a[contains(@href, "waze")]/@href')[0]
            .split("=")[1]
            .split("&")[0]
            .split(",")
        )
        hoo = poi_html.xpath('.//p[contains(text(), "Lunes")]//text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=addr.postcode,
            country_code="MX",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
