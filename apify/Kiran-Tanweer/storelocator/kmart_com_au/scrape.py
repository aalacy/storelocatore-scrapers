import random
import time
from lxml import html
from sglogging import sglog
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sgselenium.sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
import ssl


ssl._create_default_https_context = ssl._create_unverified_context

website = "https://www.kmart.com.au"
json_url = f"{website}/sitemap-core.xml"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

log = sglog.SgLogSetup().get_logger(logger_name=website)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def stringify_children(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.strip()
            if text:
                values.append(text)
    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def get_response(driver, url, count=0):
    try:
        driver.get(url)
        random_sleep(driver)
        body = html.fromstring(driver.page_source, "lxml")
        location_name = stringify_children(body, "//h1/span")
        if location_name == MISSING:
            log.debug("Error getting page")
            if count == 5:
                return None
            return get_response(driver, url, count + 1)
        return body

    except Exception as e:
        log.debug(f"Error getting page with e={e}")
        if count == 5:
            return None
        return get_response(driver, url, count + 1)


def fetch_data():
    with SgChrome(is_headless=True, user_agent=user_agent) as driver:
        driver.get(json_url)
        random_sleep(driver)
        body = html.fromstring(driver.page_source, "lxml")
        page_urls = body.xpath('//span[contains(text(), "/store-detail/")]/text()')
        log.debug(f"Total stores = {len(page_urls)}")

        count = 0

        store_number = MISSING
        location_type = MISSING
        country_code = "AU"

        for page_url in page_urls[0:50]:
            count = count + 1
            log.debug(f"{count}. scrapping {page_url} ...")
            body = get_response(driver, page_url)
            if body is None:
                log.error("Can't get response")
                continue

            location_name = stringify_children(body, "//h1/span")
            phone = stringify_children(body, '//span[@itemprop="telephone"]')
            street_address = stringify_children(
                body, '//span[@itemprop="streetAddress"]'
            )
            city = stringify_children(body, '//span[@itemprop="addressLocality"]')
            state = stringify_children(body, '//span[@itemprop="addressRegion"]')
            zip_postal = stringify_children(body, '//span[@itemprop="postalCode"]')
            latitude = body.xpath('//span[@property="latitude"]/@content')
            longitude = body.xpath('//span[@property="longitude"]/@content')
            hours_of_operation = stringify_children(
                body, '//div[@class="detail_results"]/p'
            )
            raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                MISSING, ""
            )
            raw_address = " ".join(raw_address.split())
            raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
            if raw_address[len(raw_address) - 1] == ",":
                raw_address = raw_address[:-1]

            if len(latitude) > 0:
                latitude = latitude[0]
            else:
                log.debug("No latitude found")
                continue

            if len(longitude) > 0:
                longitude = longitude[0]
            else:
                log.debug("No longitude found")
                continue

            yield SgRecord(
                locator_domain="kmart.com.au",
                store_number=store_number,
                page_url=page_url,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                state=state,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
    return []


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)
    scrape()
