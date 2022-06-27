import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "anotherbrokenegg.com"
    start_url = "https://anotherbrokenegg.com/data-locations?pager={}"

    page = 0
    while True:
        data = session.get(start_url.format(str(page))).json()
        if not data["data"]:
            break
        page += 1
        for poi_html in data["data"]:
            poi_html = etree.HTML(poi_html)
            location_name = poi_html.xpath('.//div[@class="name-location"]/a/text()')[0]
            page_url = poi_html.xpath('.//div[@class="name-location"]/a/@href')[0]
            page_url = urljoin(start_url, page_url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            street_address = loc_dom.xpath('//span[@class="address-line1"]/text()')[0]
            street_address_2 = loc_dom.xpath('//span[@class="address-line2"]/text()')
            if street_address_2:
                street_address += ", " + street_address_2[0]
            city = loc_dom.xpath('//span[@class="locality"]/text()')[0]
            state = loc_dom.xpath('//span[@class="administrative-area"]/text()')[0]
            zip_code = loc_dom.xpath('//span[@class="postal-code"]/text()')[0]
            country_code = loc_dom.xpath('//span[@class="country"]/text()')[0]
            phone = loc_dom.xpath(
                '//div[contains(text(), "Contact Phone")]/following-sibling::div/text()'
            )
            phone = phone[0] if phone else ""
            latitude = re.findall(r'map_center_latitude":"(.+?)",', loc_response.text)[
                0
            ]
            longitude = re.findall(
                r'map_center_longitude":"(.+?)",', loc_response.text
            )[0]
            hoo = loc_dom.xpath(
                '//div[contains(text(), "Hours")]/following-sibling::div/text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
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
                hours_of_operation=hoo,
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
