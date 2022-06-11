import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "guitarcenter.com"
    start_url = "https://stores.guitarcenter.com/browse/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    directories_urls = dom.xpath('//div[@class="map-list-item is-single"]/a/@href')

    for url in directories_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        urls = dom.xpath('//div[@class="map-list-item is-single"]/a/@href')
        for url in urls:
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_locations_urls = dom.xpath('//a[@class="more-details ga-link"]/@href')

            for page_url in all_locations_urls:
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)
                poi = loc_dom.xpath(
                    '//script[contains(text(), "streetAddress")]/text()'
                )[0]
                poi = json.loads(poi)

                location_name = loc_dom.xpath(
                    '//div[@class="row headerContainer indy-main-wrapper"]/div/text()'
                )
                if not location_name:
                    continue
                location_name = location_name[0]
                street_address = poi[0]["address"]["streetAddress"]
                city = poi[0]["address"]["addressLocality"]
                state = poi[0]["address"]["addressRegion"]
                zip_code = poi[0]["address"]["postalCode"]
                phone = poi[0]["address"]["telephone"]
                location_type = poi[0]["@type"]
                latitude = poi[0]["geo"]["latitude"]
                longitude = poi[0]["geo"]["longitude"]
                hours_of_operation = poi[0]["openingHours"]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code="",
                    store_number="",
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
