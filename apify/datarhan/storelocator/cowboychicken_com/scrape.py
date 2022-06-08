from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_usa
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "cowboychicken.com"
    start_url = "https://www.cowboychicken.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="list-box-con-1"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//div[@class="list-left-con"]/a[1]/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="list-left-con"]/a[1]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//p[@class="address-block"]/text()')[0].strip()
        parsed_adr = parse_address_usa(raw_address)
        country_code = parsed_adr.country
        city = parsed_adr.city
        street_address = parsed_adr.street_address_1
        if parsed_adr.street_address_2:
            street_address += " " + parsed_adr.street_address_2
        state = parsed_adr.state
        zip_code = parsed_adr.postcode
        phone = poi_html.xpath('.//a[@class="number-block"]/text()')
        phone = phone[0] if phone else ""
        latitude = poi_html.xpath(".//preceding-sibling::input[3]/@value")[0]
        longitude = poi_html.xpath(".//preceding-sibling::input[2]/@value")[0]
        hoo = poi_html.xpath('.//ul[@class="inner"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""
        if not hours_of_operation:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
