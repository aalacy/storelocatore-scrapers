import ssl
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotadeangola.com/encontrar-agente"
    domain = "toyotadeangola.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="dealer-data"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@id="dealer-name"]/text()')[0].strip()
        raw_address = poi_html.xpath('.//div[@id="dealer-adress"]/text()')[0].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath('.//div[@id="dealer-phone"]/text()')[0].strip()
        geo = poi_html.xpath('.//div[@id="dealer-map"]/text()')[0].strip().split(", ")
        with SgChrome() as driver:
            driver.get(start_url)
            sleep(5)
            elem = driver.find_element_by_xpath(
                f'//dl/dt[contains(text(), "{location_name}")]'
            )
            elem.location_once_scrolled_into_view
            elem.click()
            loc_dom = etree.HTML(driver.page_source)
            hoo = loc_dom.xpath('//p[@class="mapTime"]/text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="Angola",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
