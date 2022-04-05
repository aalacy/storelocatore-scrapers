import ssl
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from selenium.webdriver.firefox.options import Options

options = Options()
options.set_preference("geo.prompt.testing", True)
options.set_preference("geo.prompt.testing.allow", True)
options.set_preference(
    "geo.provider.network.url",
    'data:application/json,{"location": {"lat": 51.47, "lng": 0.0}, "accuracy": 100.0}',
)
options.add_argument("--headless")

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    start_url = "https://themobilegeneration.com/locations/"
    domain = "themobilegeneration.com"

    with SgFirefox(firefox_options=options, is_headless=False) as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)
        all_locations = dom.xpath("//div[@mapid]")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(15)
        next_page = driver.find_element_by_xpath('//li[@title="Next page"]/a')
        while next_page:
            next_page.click()
            dom = etree.HTML(driver.page_source)
            all_locations += dom.xpath("//div[@mapid]")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                next_page = driver.find_element_by_xpath('//li[@title="Next page"]/a')
            except Exception:
                next_page = False

        for poi_html in all_locations:
            location_name = poi_html.xpath(".//strong/a/text()")[0]
            raw_address = poi_html.xpath('.//div[@class="wpgmza-address"]/text()')[
                0
            ].split(", ")
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
            hoo = poi_html.xpath('.//p[b[contains(text(), "M-F")]]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            geo = poi_html.xpath("@data-latlng")[0].split(", ")

            item = SgRecord(
                locator_domain=domain,
                page_url="https://themobilegeneration.com/locations/",
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[1],
                state=raw_address[2].split()[0],
                zip_postal=raw_address[2].split()[-1],
                country_code=raw_address[3],
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
