import urllib.parse
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "ironmountain.com"
    start_url = "https://locations.ironmountain.com/"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations_urls = dom.xpath('//div[@class="countries-list-wrap"]//a/@href')
    for location_url in all_locations_urls:
        location_response = session.get(urllib.parse.urljoin(start_url, location_url))
        location_dom = etree.HTML(location_response.text)

        all_points = location_dom.xpath('//ul[@class="map-list"]//a/@href')
        for point_url in all_points:
            point_response = session.get(urllib.parse.urljoin(start_url, point_url))
            point_dom = etree.HTML(point_response.text)

            all_point_locations = point_dom.xpath('//ul[@class="map-list"]/li')
            for point_location in all_point_locations:
                store_url = point_location.xpath(".//a/@href")[0]
                loc_response = session.get(store_url)
                loc_dom = etree.HTML(loc_response.text)

                location_name = point_location.xpath(".//a/text()")[0]
                location_name = location_name.strip() if location_name else "<MISSING>"
                street_address = loc_dom.xpath(
                    '//meta[@property="business:contact_data:street_address"]/@content'
                )
                street_address = street_address[0] if street_address else ""
                if not street_address:
                    continue
                city = loc_dom.xpath(
                    '//meta[@property="business:contact_data:locality"]/@content'
                )
                city = city[0] if city else "<MISSING>"
                state = loc_dom.xpath(
                    '//meta[@property="business:contact_data:region"]/@content'
                )
                state = state[0] if state and len(state[0].strip()) > 1 else "<MISSING>"
                zip_code = loc_dom.xpath(
                    '//meta[@property="business:contact_data:postal_code"]/@content'
                )
                zip_code = (
                    zip_code[0] if zip_code and len(zip_code[0]) > 1 else "<MISSING>"
                )
                if zip_code == "00000":
                    zip_code = "<MISSING>"
                country_code = loc_dom.xpath(
                    '//meta[@property="business:contact_data:country_name"]/@content'
                )
                country_code = country_code[0] if country_code else "<MISSING>"
                store_number = response.url.raw[-1].decode("utf-8").split("/")[-2]
                phone = loc_dom.xpath(
                    '//meta[@property="business:contact_data:phone_number"]/@content'
                )
                phone = phone[0] if phone else "<MISSING>"
                location_type = "<MISSING>"
                latitude = loc_dom.xpath(
                    '//meta[@property="place:location:latitude"]/@content'
                )
                latitude = latitude[0] if latitude else "<MISSING>"
                longitude = loc_dom.xpath(
                    '//meta[@property="place:location:longitude"]/@content'
                )
                longitude = longitude[0] if longitude else "<MISSING>"
                hours_of_operation = "<MISSING>"

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
