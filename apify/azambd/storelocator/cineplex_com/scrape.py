from sgpostal.sgpostal import parse_address_intl
from lxml import html
import time
import random

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests

from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


website = "https://www.cineplex.com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception as e:
        log.info(f"{e}")
        pass


def random_sleep(driver, start=5, limit=6):
    driver_sleep(driver, random.randint(start, start + limit))


def request_with_retries(driver, url):
    return driver.get(url)


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
        log.info(f"Address Err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fix_string(body, xpath):
    data = body.xpath(xpath)
    if len(data) == 0:
        return MISSING
    data = " ".join(data)
    data = data.replace("\r", " ").replace("\n", " ").strip()
    data = (" ".join(data.split())).strip()
    return data


def fetch_stores(driver):
    page = 0
    pageUrls = []
    while True:
        page = page + 1
        request_with_retries(
            driver,
            f"{website}/Theatres/TheatreListings?LocationURL=calgary&Range=5000&page={page}",
        )
        body = html.fromstring(driver.page_source, "lxml")
        random_sleep(driver)
        urls = body.xpath('//div[contains(@class, "theatre-text")]/a/@href')
        if len(urls) == 0:
            break
        for url in urls:
            if url not in pageUrls:
                pageUrls.append(url)
        log.debug(f"Page {page}. total url ={len(urls)}; pageUrls={len(pageUrls)}")
    return pageUrls


def fetch_data(driver, http):
    urls = fetch_stores(driver)
    log.info(f"Total stores = {len(urls)}")

    count = 0
    for url in urls:
        count = count + 1
        page_url = f"{website}{url}"
        log.debug(f"{count}. scrapping {page_url} ...")
        response = http.get(page_url)
        body = html.fromstring(response.text, "lxml")

        store_number = MISSING
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
        hours_of_operation = MISSING

        location_name = fix_string(body, "//h1/text()")
        raw_address = fix_string(
            body, '//div[contains(@class, "theatre-details-page-address")]/a/text()'
        )
        phone = fix_string(
            body, '//div[contains(@class, "theatre-details-page-phone")]/a/text()'
        )

        street_address, city, state, zip_postal = get_address(raw_address)
        country_code = "CA"

        yield SgRecord(
            locator_domain=website,
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
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    count = 0
    with SgRequests() as http:
        with SgChrome() as driver:
            with SgWriter(
                deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)
            ) as writer:
                for rec in fetch_data(driver, http):
                    writer.write_row(rec)
                    count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
