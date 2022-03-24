from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.stayinns.com/hotels"
    domain = "countryhearth.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//article[@role="article"]')
    next_page = dom.xpath('//a[@rel="next"]/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//article[@role="article"]')
        next_page = dom.xpath('//a[@rel="next"]/@href')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h3/a/@href")[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath(".//h3/a/span/text()")
        location_name = location_name[0] if location_name else ""
        street_address = poi_html.xpath('.//span[@class="address-line1"]/text()')
        street_address = street_address[0] if street_address else ""
        city = poi_html.xpath('.//span[@class="locality"]/text()')
        city = city[0] if city else ""
        state = poi_html.xpath('.//span[@class="administrative-area"]/text()')
        state = state[0] if state else ""
        zip_code = poi_html.xpath('.//span[@class="postal-code"]/text()')
        zip_code = zip_code[0] if zip_code else ""
        country_code = poi_html.xpath('.//span[@class="country"]/text()')
        country_code = country_code[0] if country_code else ""
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""

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
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
