from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.krystal.com/locations/all/"
    domain = "krystal.com"
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    with SgFirefox() as driver:
        for code in all_codes:
            driver.get(start_url)
            driver.find_element_by_xpath(
                '//input[@placeholder="Search zip, city, or state"]'
            ).send_keys(code)
            sleep(10)
            dom = etree.HTML(driver.page_source)

            all_locations = dom.xpath("//div[@data-loc]")
            for poi_html in all_locations:
                url = poi_html.xpath('.//a[contains(text(), "Store Details")]/@href')[0]
                page_url = urljoin(start_url, url)
                loc_response = session.get(page_url)
                try:
                    loc_dom = etree.HTML(loc_response.text)
                except Exception:
                    continue

                location_name = loc_dom.xpath("//h1/text()")[0]
                raw_address = loc_dom.xpath("//h1/following-sibling::p[1]/text()")[
                    0
                ].split(", ")
                phone = (
                    poi_html.xpath('.//a[contains(@href, "tel")]/@href')[0]
                    .split(":")[-1]
                    .strip()
                )
                store_number = poi_html.xpath("@data-loc")[0]
                days = loc_dom.xpath('//div[@class="day flex"]/p/span/text()')
                hours = loc_dom.xpath('//div[@class="time flex"]/p/span/text()')
                hoo = " ".join(list(map(lambda d, h: d + " " + h, days, hours)))

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=raw_address[0],
                    city=raw_address[1],
                    state=raw_address[-1].split()[0],
                    zip_postal=raw_address[-1].split()[-1],
                    country_code="",
                    store_number=store_number,
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
