from lxml import etree
from time import sleep
from random import uniform

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    start_url = (
        "https://www.groceryoutlet.com/store-locator?store_location={}&store_region="
    )
    domain = "groceryoutlet.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    with SgFirefox() as driver:
        for code in all_codes:
            driver.get(start_url.format(code))
            sleep(uniform(5, 30))
            dom = etree.HTML(driver.page_source)

            all_locations = dom.xpath("//li[@data-store-number]")
            for poi_html in all_locations:
                location_name = poi_html.xpath(".//h6/text()")[0]
                page_url = poi_html.xpath('.//a[contains(text(), "See This")]/@href')[0]
                raw_address = poi_html.xpath(".//address/text()")
                store_number = poi_html.xpath("@data-store-number")[0]
                phone = poi_html.xpath('.//a[@class="store-phone d-block"]/text()')[0]
                hoo = poi_html.xpath(
                    './/div[strong[contains(text(), "Store Hours")]]/following-sibling::div/text()'
                )
                hoo = " ".join(hoo)

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=raw_address[0],
                    city=raw_address[-1].split(", ")[0],
                    state=raw_address[-1].split(", ")[-1].split()[0],
                    zip_postal=raw_address[-1].split(", ")[-1].split()[-1],
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
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
