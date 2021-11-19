import jstyleson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "underarmour.ca"
    start_url = "http://store-locations.underarmour.com/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = []
    states_urls = dom.xpath(
        '//h3[contains(text(), "Canada")]/following-sibling::ul//a/@href'
    )
    for url in states_urls:
        state_response = session.get(url)
        state_dom = etree.HTML(state_response.text)
        cities_urls = state_dom.xpath('//a[@linktrack="State index"]/@href')
        for c_url in cities_urls:
            city_response = session.get(c_url)
            city_dom = etree.HTML(city_response.text)
            all_locations += city_dom.xpath(
                '//a[@data-gaact="Click_to_Store_Details"]/@href'
            )

    for url in list(set(all_locations)):
        loc_response = session.get(url)
        loc_dom = etree.HTML(loc_response.text)
        store_data = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "streetAddress")]/text()'
        )
        poi = jstyleson.loads(store_data[0])

        store_url = url
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["@id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["telephone"]
        if phone:
            phone = phone if phone != "#" else ""
        if not phone:
            continue
        location_type = poi["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["openingHoursSpecification"]:
            day = elem["dayOfWeek"][0]
            opens = elem["opens"]
            closes = elem["closes"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
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
