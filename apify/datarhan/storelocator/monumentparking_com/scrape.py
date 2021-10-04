from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    start_url = "https://www.monumentparking.com/locations.html"
    domain = "monumentparking.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=5
    )
    for code in all_codes:
        with SgChrome() as driver:
            driver.get(start_url)
            driver.find_element_by_id("address").clear()
            driver.find_element_by_id("address").send_keys(code)
            sleep(1)
            driver.find_element_by_xpath('//input[@value="Search"]').click()
            sleep(2)
            try:
                dom = etree.HTML(driver.page_source)
            except Exception:
                continue
            all_locations = dom.xpath('//tr[@class="result"]')
            for poi_html in all_locations:
                location_name = poi_html.xpath(
                    './/td[@class="parking-address"]/a/text()'
                )[0].split(" - ")[0]
                raw_address = (
                    poi_html.xpath('.//td[@class="parking-address"]/a/text()')[0]
                    .split(" - ")[-1]
                    .split(", ")
                )
                phone = (
                    poi_html.xath('.//td[@class="parking-address"]/text()')[-1]
                    .split(":")[-1]
                    .strip()
                )
                hoo = poi_html.xpath('.//td[@class="hours-operation"]//text()')
                hoo = [e.strip() for e in hoo if e.strip()]
                hoo = " ".join(hoo)

                item = SgRecord(
                    locator_domain=domain,
                    page_url=start_url,
                    location_name=location_name,
                    street_address=raw_address[0],
                    city=raw_address[1],
                    state=raw_address[-1].split()[0],
                    zip_postal=raw_address[-1].split()[-1],
                    country_code="",
                    store_number="",
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
