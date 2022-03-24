import re
import random
import ssl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from lxml import html
from sgpostal.sgpostal import parse_address_intl
import time
from xml.etree import ElementTree as ET
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-es:{}@proxy.apify.com:8000/"

ssl._create_default_https_context = ssl._create_unverified_context

website = "https://www.telepizza.es"
sitemap_url = f"{website}/sitemap.xml"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests(proxy_country="es")
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=3, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def fetch_stores():
    response = request_with_retries(sitemap_url)
    page_urls = []
    root = ET.fromstring(response.text)
    for elem in root:
        for var in elem:
            if "loc" in var.tag and "https://www.telepizza.es/pizzeria/" in var.text:
                page_urls.append(var.text)
    return page_urls


def fetch_store(driver, page_url):
    try:
        driver.get(page_url)
        return html.fromstring(driver.page_source, "lxml"), driver.page_source
    except Exception as e:
        log.error(f"Error msg={e}")
        pass
    return None, None


def stringify_nodes(body, xpath):
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

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Address Missing : {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_txt(response, var):
    try:
        return response.split(f"var {var} =")[1].split(";")[0].strip()
    except Exception:
        pass
    return MISSING


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetch_data(driver):
    page_urls = fetch_stores()
    log.info(f"Total stores = {len(page_urls)}")

    location_type = MISSING
    country_code = "ES"

    count = 0
    for page_url in page_urls:
        count = count + 1
        log.info(f"{count}. scrapping {page_url}...")
        store_number = page_url.split("-")
        store_number = store_number[len(store_number) - 1]
        body, response = fetch_store(driver, page_url)
        if body is None or response is None:
            log.error("Can't scrape")
            continue
        location_name = stringify_nodes(body, '//h1[contains(@class, "heading-xl")]')
        raw_address = stringify_nodes(
            body, '//div[contains(@class, "mod_generic_promotion shopTitle")]/address'
        )
        if location_name == MISSING or raw_address == MISSING:
            log.error("Can't scrape")
            continue
        street_address, city, state, zip_postal = get_address(raw_address)
        phone = get_phone(
            stringify_nodes(
                body,
                '//span[contains(@itemprop, "telephone")]/a[contains(@href, "tel")]',
            )
        )
        hoo = stringify_nodes(
            body,
            '//div[contains(@class, "hours")]/div[contains(@class, "columns")][2]/table',
        )
        hours_of_operation = hoo.split("festivo")[0]

        latitude = get_txt(response, "lat")
        longitude = get_txt(response, "lng")

        if latitude == "0" or longitude == "0":
            latitude = MISSING
            longitude = MISSING

        yield SgRecord(
            locator_domain="telepizza.es",
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
    with SgChrome() as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
