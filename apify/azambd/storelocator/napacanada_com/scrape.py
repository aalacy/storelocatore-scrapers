from sgselenium import SgChrome
import tenacity
import time
import json
from lxml import etree
from urllib.parse import urljoin

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

from sglogging import sglog
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "napacanada.com"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

start_url = "https://www.napacanada.com/en/store-finder?q=H1N+3E2&page=7"


@tenacity.retry(wait=tenacity.wait_fixed(3))
def get_with_retry(driver, url):
    driver.get(url)
    driver.set_page_load_timeout(20)
    return driver.page_source


def extract_details(html):
    loc_dom = etree.HTML(html)
    scripts = loc_dom.xpath('//script[@type="application/ld+json"]/text()')

    for script in scripts:
        if "address" in script:
            return json.loads(script)


def fetch_data():

    with SgChrome(is_headless=True, user_agent=user_agent) as driver:
        driver.get(start_url)
        time.sleep(30)
        htmlSource = driver.page_source
        dom = etree.HTML(htmlSource)
        all_locations = dom.xpath('//li[@class="aadata-store-item"]')
        log.info(f"Total Locations: {len(all_locations)}")
        for poi_html in all_locations:
            store_url = poi_html.xpath('.//a[@class="storeWebsiteLink"]/@href')[0]
            store_url = urljoin(start_url, store_url)
            html = get_with_retry(driver, store_url)
            poi = extract_details(html)
            location_name = poi["name"]
            log.info(f"Now Crawling: {location_name} => {store_url}")
            phone = poi["telephone"]
            phone = phone if phone else "<MISSING>"
            hoo = []
            for elem in poi["openingHoursSpecification"]:
                day = elem["dayOfWeek"][0]
                opens = elem["opens"]
                closes = elem["closes"]
                hoo.append(f"{day} {opens} - {closes}")
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            item = SgRecord(
                locator_domain=DOMAIN,
                page_url=store_url,
                location_name=location_name,
                street_address=poi["address"]["streetAddress"],
                city=poi["address"]["addressLocality"],
                state=poi["address"]["addressRegion"],
                zip_postal=poi["address"]["postalCode"],
                country_code=poi["address"]["addressCountry"],
                store_number=poi["@id"],
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=poi["geo"]["latitude"],
                longitude=poi["geo"]["longitude"],
                hours_of_operation=hours_of_operation,
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
