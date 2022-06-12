import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "grimaldispizzeria.com"
    start_url = "https://www.grimaldispizzeria.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(text(), "More Details")]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[-1]
        poi = json.loads(poi)

        location_name = loc_dom.xpath('//div[@class="container"]/h1/text()')
        location_name = location_name[0] if location_name else ""
        street_address = poi["address"]["streetAddress"]
        location_type = poi["@type"]
        if loc_dom.xpath('//div[@class="store_copy coming_soon_status"]'):
            continue
        state = poi["address"]["addressRegion"]
        city = poi["address"]["addressLocality"]
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["addressCountry"]
        phone = poi.get("telephone")
        hours_of_operation = loc_dom.xpath(
            '//div[div[contains(text(), "Hours")]]/text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""

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
            location_type=location_type,
            latitude="",
            longitude="",
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
