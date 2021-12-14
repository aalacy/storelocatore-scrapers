from sgpostal.sgpostal import parse_address_intl
import random
import ssl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from sgselenium.sgselenium import SgChrome
import time
from lxml import html
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

ssl._create_default_https_context = ssl._create_unverified_context

website = "https://www.gtbank.com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(driver, url, text, retry=0):
    driver.get(url)
    random_sleep(driver)
    response = driver.page_source
    if text in response:
        return html.fromstring(response, "lxml")

    if text not in response and retry == 4:
        return None
    return request_with_retries(driver, url, text, retry + 1)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=3, limit=5):
    driver_sleep(driver, random.randint(start, start + limit))


def fetch_stores(driver, retry=0):
    body = request_with_retries(driver, f"{website}/branches", "branches-link")
    urls = body.xpath('//a[contains(@class, "branches-link")]/@href')
    return urls
    if len(urls) > 0:
        return urls
    if len(urls) == 0 and retry == 4:
        return []
    return fetch_stores(driver, retry + 1)


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
    return " ".join(values)


def get_dir_url(list):
    try:
        return list[0].split("destination=")[1].split("&")[0].replace("%20", " ")
    except Exception as e:
        log.info(f"get dir Err: {e}")
        return ""


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            country_code = data.country

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            if country_code is None or len(country_code) == 0:
                country_code = MISSING
            return street_address, city, state, zip_postal, country_code
    except Exception as e:
        log.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING, MISSING


def fetch_data(driver):
    page_urls = fetch_stores(driver)
    log.info(f"Total stores = {len(page_urls)}")
    count = 0
    for page_url in page_urls:
        count = count + 1
        log.debug(f"{count}. fetching {page_url} ...")

        store_number = MISSING
        location_type = MISSING
        phone = MISSING

        body = request_with_retries(driver, page_url, "Get Directions")

        latlng = body.xpath('//div[contains(@id, "locator-entry")]/@data-dna')[0]
        coords = json.loads(latlng)

        latitude = coords[0]["locations"][0]["lat"] or MISSING
        longitude = coords[0]["locations"][0]["lng"] or MISSING

        location_name = stringify_children(
            body, '//div[contains(@class, "branch-info-title")]/span'
        )
        raw_address = stringify_children(
            body, '//div[contains(@class, "branch-info-address")]'
        )
        hours_of_operation = stringify_children(
            body, '//div[contains(@class, "branch-info-content-item")]/ul/li/span'
        )
        street_address, city, state, zip_postal, country_code = get_address(raw_address)

        yield SgRecord(
            locator_domain="gtbank.com",
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code="NG",
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
    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
