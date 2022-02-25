import ssl
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    start_url = "https://www.monumentparking.com/locations.html"
    domain = "monumentparking.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=5
    )
    for code in all_codes:
        with SgChrome() as driver:
            try:
                driver.get(start_url)
            except Exception:
                continue
            try:
                driver.find_element_by_id("address").clear()
            except Exception:
                continue
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
