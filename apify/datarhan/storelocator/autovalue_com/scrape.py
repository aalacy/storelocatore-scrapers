import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "autovalue.com"
    start_url = "https://locations.autovalue.com/"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text.split('.dtd">')[-1])
    all_urls = dom.xpath("//a[@data-gaact]/@href")
    for url in all_urls:
        response = session.get(url)
        dom = etree.HTML(response.text.split('.dtd">')[-1])
        sub_urls = dom.xpath("//a[@data-gaact]/@href")
        for sub_url in sub_urls:
            response = session.get(sub_url)
            dom = etree.HTML(response.text.split('.dtd">')[-1])
            all_locations += dom.xpath('//a[@linktrack="Landing page"]/@href')

    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "AutoPartsStore")]/text()')[0]
        poi = demjson.decode(poi)

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
        store_url = poi["url"]
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for elem in poi["openingHoursSpecification"]:
            day = elem["dayOfWeek"][0]
            opens = elem["opens"]
            closes = elem["closes"]
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

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
