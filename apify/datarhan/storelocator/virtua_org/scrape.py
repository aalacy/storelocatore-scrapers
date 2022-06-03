from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "virtua.org"
    start_url = "https://www.virtua.org/locations/search-results"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@class="search-listing-item__text-content"]/h3/a/@href'
    )
    next_page = dom.xpath('//li[@class="pagination_button next-btn "]/a/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//div[@class="search-listing-item__text-content"]/h3/a/@href'
        )
        next_page = dom.xpath('//li[@class="pagination_button next-btn "]/a/@href')

    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        if not loc_dom.xpath("//@data-map-coords"):
            continue

        location_name = loc_dom.xpath('//h1[@itemprop="name"]/text()')
        location_name = location_name[0].split(" - ")[0] if location_name else ""
        street_address = loc_dom.xpath('//p[@itemprop="streetAddress"]/text()')
        street_address = street_address[0].strip() if street_address else ""
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else ""
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0].strip() if state else ""
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else ""
        phone = loc_dom.xpath('//a[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else ""
        latitude = loc_dom.xpath("//@data-map-coords")[0].split(",")[0]
        longitude = loc_dom.xpath("//@data-map-coords")[0].split(",")[-1]
        hours_of_operation = loc_dom.xpath(
            '//h3[contains(text(), "Hours")]/following-sibling::div[1][@class="accordion-content rta"]/div[1]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            ", ".join(hours_of_operation)
            .split("visiting is")[0]
            .replace("Although ", "")
        )
        hours_of_operation = hours_of_operation if hours_of_operation else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="US",
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
