import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "novotel.accor.com"
    start_url = "https://novotel.accor.com/gb/world/hotels-novotel-monde.shtml"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_zones = dom.xpath(
        '//div[@id="paginator-list-core"]//a[@class="Teaser-link"]/@href'
    )
    for url in all_zones:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//div[@id="paginator-list-hotel"]//a[@class="Teaser-link"]/@href'
        )
        all_countries = dom.xpath(
            '//div[@id="paginator-list-core"]//a[@class="Teaser-link"]/@href'
        )
        for url in all_countries:
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath(
                '//div[@id="paginator-list-hotel"]//a[@class="Teaser-link"]/@href'
            )
            all_locations += dom.xpath('//a[contains(@href, "/hotel/")]/@href')
            all_cities = dom.xpath(
                '//div[@id="paginator-list-core"]//a[@class="Teaser-link"]/@href'
            )
            for url in all_cities:
                response = session.get(url)
                dom = etree.HTML(response.text)
                all_locations += dom.xpath(
                    '//div[@id="paginator-list-hotel"]//a[@class="Teaser-link"]/@href'
                )
                all_locations += dom.xpath('//a[contains(@href, "/hotel/")]/@href')
                all_subs = dom.xpath(
                    '//div[@id="paginator-list-core"]//a[@class="Teaser-link"]/@href'
                )
                for url in all_subs:
                    response = session.get(url)
                    dom = etree.HTML(response.text)
                    all_locations += dom.xpath(
                        '//div[@id="paginator-list-hotel"]//a[@class="Teaser-link"]/@href'
                    )

    for url in list(set(all_locations)):
        poi_url = urljoin(start_url, url)
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "postalCode")]/text()'
        )
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            street = loc_dom.xpath('//meta[@property="og:street-address"]/@content')
            street = street[0] if street else ""
            city = poi["address"]["addressLocality"]
            city = city if city else ""
            state = ""
            zip_code = poi["address"].get("postalCode")
            zip_code = zip_code if zip_code else ""
            phone = poi["telephone"]
            location_type = poi["@type"]
            country_code = poi["address"]["addressCountry"]
            country_code = country_code if country_code else ""
        else:
            poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')[0]
            poi = json.loads(poi)

            location_name = poi["hotelName"]
            street = poi["streetAddress"]
            city = poi["city"]
            state = SgRecord.MISSING
            zip_code = SgRecord.MISSING
            phone = loc_dom.xpath('//a[@class="infos__phone"]/text()')
            phone = phone[0].strip() if phone else ""
            location_type = SgRecord.MISSING
            country_code = poi["country"]
        if "Novotel" not in location_name:
            continue
        latitude = loc_dom.xpath('//meta[@property="og:latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@property="og:longitude"]/@content')[0]
        if not phone:
            phone = loc_dom.xpath('//a[@class="infos__phone text-link"]/text()')[
                0
            ].strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=poi_url,
            location_name=location_name,
            street_address=street,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=poi_url.split("/")[-2],
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
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
