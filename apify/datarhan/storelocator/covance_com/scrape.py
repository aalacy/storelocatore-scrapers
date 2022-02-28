from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    cities_to_filter = [
        "Buenos Aires",
        "Rueil Malmaison",
        "Seoul",
        "Singapore",
        "Zurich",
    ]

    domain = "covance.com"
    start_url = "https://www.covance.com/locations.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="locations-results-row"]')

    for poi_html in all_locations[1:]:
        location_name = poi_html.xpath('.//li[@class="name"]/text()')
        if not location_name:
            continue
        location_name = (
            location_name[0].replace("<", "") if location_name else "<MISSING>"
        )
        if "headquarters" in location_name.lower():
            continue
        raw_address = poi_html.xpath('.//li[@class="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        full_addr = (
            " ".join(raw_address)
            .replace("\n", " ")
            .replace("\t", " ")
            .split("44 203 810")[0]
        )
        addr = parse_address_intl(full_addr)
        country_code = addr.country
        if country_code not in ["Usa", "<MISSING>", "UK", "United Kingdom"]:
            continue
        city = addr.city
        city = city.strip() if city else "<MISSING>"
        if city in cities_to_filter:
            continue
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        state = addr.state
        zip_code = addr.postcode
        phone = poi_html.xpath('.//li[@class="phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address=full_addr,
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
