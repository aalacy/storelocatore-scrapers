from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://cinnabonrussia.com/locations/"
    domain = "cinnabonrussia.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="loc-results-item location-item"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//div[@class="loc-res-phone margin-top"]/a/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else ""
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[-1].strip() if phone else ""
        if store_url:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            if not phone:
                phone = loc_dom.xpath(
                    '//div[contains(text(), "Телефон:")]/following-sibling::div/text()'
                )
                phone = phone[0] if phone else ""

        location_name = poi_html.xpath('.//a[@class="store"]/span/span/text()')[0]
        raw_addr = poi_html.xpath('.//a[@class="directions-link store"]/span/text()')
        if raw_addr:
            addr = parse_address_intl(raw_addr[0])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city.replace("Г.", "").replace("г.", "") if addr.city else ""
            state = addr.state
            zip_code = addr.postcode
        else:
            street_address = ""
            city = ""
            state = ""
            zip_code = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="RU",
            store_number=poi_html.xpath(".//a/@data-store")[0],
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address=raw_addr,
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
