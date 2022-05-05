from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    domain = "buildwithbmc.com"
    start_url = "https://www.buildwithbmc.com/bmc/store-finder"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    with SgFirefox() as driver:
        for code in all_codes:
            driver.get(start_url)
            sleep(3)
            try:
                driver.find_element_by_xpath(
                    '//div[contains(text(), "100 Miles")]'
                ).click()
            except Exception:
                pass
            sleep(2)
            q = driver.find_element_by_xpath('//input[@id="storelocator-query"]')
            q.send_keys(code)
            sleep(2)
            q.submit()
            sleep(5)
            dom = etree.HTML(driver.page_source)
            all_locations = dom.xpath('//div[@class="section2 search-result-item"]')
            for poi_html in all_locations:
                url = poi_html.xpath('.//a[contains(text(), "More")]/@href')[0]
                page_url = urljoin(start_url, url)
                location_name = poi_html.xpath(".//h2/text()")[0][3:]
                store_number = poi_html.xpath(
                    './/div[@class="pull-right white-font"]/text()'
                )[0].split("#")[-1]
                raw_address = poi_html.xpath(".//p/text()")
                raw_address = [
                    e.replace("\xa0", "").strip() for e in raw_address if e.strip()
                ]
                phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
                location_type = poi_html.xpath(
                    './/h3[contains(text(), "Facility Type")]/following-sibling::div//text()'
                )
                location_type = [e.strip() for e in location_type if e.strip()]
                location_type = ", ".join(location_type)
                latitude = poi_html.xpath(".//@data-latitude")[0]
                longitude = poi_html.xpath(".//@data-longitude")[0]
                hoo = poi_html.xpath(
                    './/div[h3[contains(text(), "Hours")]]/following-sibling::div//text()'
                )
                hoo = " ".join(
                    " ".join(
                        [e.replace("\n", "").strip() for e in hoo if e.strip()]
                    ).split()
                )

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=raw_address[0],
                    city=raw_address[1].split(",")[0],
                    state=raw_address[1].split(",")[-1].split()[0],
                    zip_postal=raw_address[1].split(",")[-1].split()[-1],
                    country_code="",
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
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
