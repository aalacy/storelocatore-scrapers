from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "ryder.com"
    start_urls = [
        "https://ryder.com/locations/USA",
        "https://ryder.com/locations/can",
        "https://ryder.com/locations/uk",
    ]

    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_state_urls = dom.xpath(
            '//a[@class="js-grab-click js--location__link"]/@href'
        )
        for state_url in all_state_urls:
            state_response = session.get("https://ryder.com" + state_url)
            state_dom = etree.HTML(state_response.text)
            cities_url = state_dom.xpath(
                '//a[@class="js-grab-click js--location__link location__link--cities"]/@href'
            )
            for city_url in cities_url:
                city_response = session.get("https://ryder.com" + city_url)
                city_dom = etree.HTML(city_response.text)
                locations_html = city_dom.xpath('//div[@class="location__item"]')
                for l_html in locations_html:
                    store_url = "https://ryder.com" + l_html.xpath(".//a/@href")[0]
                    loc_response = session.get(store_url)
                    loc_dom = etree.HTML(loc_response.text)

                    location_name = l_html.xpath(
                        './/span[@itemprop="addressName"]/text()'
                    )
                    location_name = (
                        location_name[0].strip() if location_name else "<MISSING>"
                    )
                    street_address = l_html.xpath(
                        './/span[@itemprop="streetAddress"]/text()'
                    )
                    street_address = (
                        " ".join(street_address).strip()
                        if street_address
                        else "<MISSING>"
                    )
                    city = l_html.xpath('.//span[@itemprop="addressLocality"]/text()')
                    city = city[0].replace(",", "").strip() if city else "<MISSING>"
                    state = l_html.xpath('.//span[@itemprop="addressRegion"]/text()')
                    state = state[0].strip() if state else "<MISSING>"
                    if state == "UK":
                        state = "<MISSING>"
                    zip_code = l_html.xpath('.//span[@itemprop="postalCode"]/text()')
                    zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
                    country_code = l_html.xpath(
                        './/span[@itemprop="addressCountry"]/text()'
                    )
                    country_code = (
                        country_code[0].strip() if country_code else "<MISSING>"
                    )
                    store_number = location_name.split("#")[-1].strip()
                    phone = l_html.xpath('.//span[@itemprop="telephone"]/text()')
                    phone = phone[0].strip() if phone else ""
                    phone = phone if phone else "<MISSING>"
                    location_type = ", ".join(
                        loc_dom.xpath('//ul[@class="location__services"]/li/text()')
                    )
                    latitude = l_html.xpath(".//a/@data-lat")
                    latitude = latitude[0] if latitude else "<MISSING>"
                    longitude = l_html.xpath(".//a/@data-lng")
                    longitude = longitude[0] if longitude else "<MISSING>"
                    hours_of_operation = l_html.xpath(
                        './/ul[contains(@class, "services--hours")]/li/text()'
                    )
                    hours_of_operation = (
                        " ".join(hours_of_operation)
                        if hours_of_operation
                        else "<MISSING>"
                    )

                    if state.isnumeric():
                        new_state = zip_code
                        zip_code = state
                        state = new_state

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
