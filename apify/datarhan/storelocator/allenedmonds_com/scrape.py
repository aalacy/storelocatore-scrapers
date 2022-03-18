from time import sleep
from lxml import etree
from urllib.parse import urljoin
from selenium.webdriver.common.keys import Keys

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    domain = "allenedmonds.com"
    start_url = "https://www.allenedmonds.com/stores"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    with SgFirefox() as driver:
        for code in all_codes:
            driver.get(start_url)
            sleep(5)
            driver.find_element_by_name("zip").send_keys(code)
            sleep(2)
            driver.find_element_by_name("zip").send_keys(Keys.ENTER)
            sleep(3)
            dom = etree.HTML(driver.page_source)

            all_locations = dom.xpath(
                '//a[span[contains(text(), "Store Details")]]/@href'
            )
            for page_url in all_locations:
                if "/stores/null" in page_url:
                    continue
                page_url = urljoin(start_url, page_url)
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)

                location_name = loc_dom.xpath("//h1/text()")[0]
                raw_address = loc_dom.xpath(
                    '//div[@class="StoreListResult_address"]/span/text()'
                )
                if len(raw_address) > 2:
                    raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
                phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
                hoo = loc_dom.xpath(
                    '//strong[contains(text(), "Store Hours")]/following-sibling::ul[1]//text()'
                )
                hoo = " ".join([e.strip() for e in hoo if e.strip()])

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=raw_address[0],
                    city=raw_address[1].split(", ")[0],
                    state=raw_address[1].split(", ")[-1].split()[0],
                    zip_postal=raw_address[1].split(", ")[-1].split()[-1],
                    country_code="",
                    store_number=page_url.split("/")[-2],
                    phone=phone,
                    location_type="",
                    latitude="",
                    longitude="",
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
