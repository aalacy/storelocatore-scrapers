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

        location_name = poi["name"].replace("&#39;", "'").replace("&amp;", "&")
        street_address = poi["address"]["streetAddress"]
        city = poi["address"]["addressLocality"]
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["addressCountry"]
        store_number = poi["@id"]
        store_url = poi["url"]
        phone = poi["telephone"]
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
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
