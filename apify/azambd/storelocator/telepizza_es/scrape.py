import re
from lxml import etree
from urllib.parse import urljoin
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = sglog.SgLogSetup().get_logger("swatch.com")


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    session = SgRequests()
    class_name = "heading-xl"
    start_url = "https://www.telepizza.es/pizzerias"
    domain = "telepizza.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    logger.info(f"{start_url} : Response 1: {response}")
    dom = etree.HTML(response.text)
    all_areas = dom.xpath('//ul[@class="areas"]/li/a/@href')
    for url in all_areas:
        response = session.get(urljoin(start_url, url))
        logger.info(f"{urljoin(start_url, url)} >> Response 2: {response}")
        dom = etree.HTML(response.text)
        all_cities = dom.xpath('//ul[@class="cities"]/li/a/@href')
        logger.info(f"Total Cities: {len(all_cities)}")
        for url in all_cities:
            url = urljoin(start_url, url)
            response = session.get(url)
            logger.info(f"{urljoin(start_url, url)} >> Response 3: {response}")
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//ul[@class="list"]/li')

            for poi_html in all_locations:
                page_url = poi_html.xpath('.//a[@class="moreInfoLinkFromList"]/@href')
                if not page_url:
                    page_url = poi_html.xpath("//@urltienda")
                page_url = urljoin(start_url, page_url[0])

                logger.info(f" Crawling by selenium {page_url}")
                try:
                    driver = get_driver(page_url, class_name, driver=None)
                except Exception:
                    driver = get_driver(page_url, class_name)

                loc_html = driver.page_source

                loc_dom = etree.HTML(loc_html)
                location_name = poi_html.xpath(".//h2/text()")[0]
                raw_address = poi_html.xpath('.//p[@class="prs"]/text()')
                zip_code = loc_dom.xpath("//address/span[2]/text()")[0]
                logger.info(f"Zip Code: {zip_code}")
                city = raw_address[-1]
                if city.startswith("."):
                    city = city[1:]
                phone = poi_html.xpath('.//p[span[@class="i_phone"]]/span[2]/text()')[0]
                latitude = re.findall("lat = (.+?);", loc_html)[0]
                longitude = re.findall("lng = (.+?);", loc_html)[0]
                hoo = loc_dom.xpath(
                    '//h4[contains(text(), "A recoger")]/following-sibling::table//text()'
                )
                hoo = " ".join([e.strip() for e in hoo if e.strip()])

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=raw_address[0],
                    city=city,
                    state="",
                    zip_postal=zip_code,
                    country_code="ES",
                    store_number="",
                    phone=phone,
                    location_type="",
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hoo,
                )

                yield item

            driver.quit()


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
