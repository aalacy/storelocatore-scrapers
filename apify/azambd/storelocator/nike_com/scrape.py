import re
from sgpostal.sgpostal import parse_address_intl
from lxml import html
import time
import random
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgscrape.pause_resume import CrawlStateSingleton
from sgselenium.sgselenium import SgChrome

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


website = "https://www.nike.com"
store_url = f"{website}/retail/directory"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=1, limit=2):
    driver_sleep(driver, random.randint(start, start + limit))


def request_with_retries(driver, url, tried=1):
    try:
        driver.get(url)
        random_sleep(driver)
        return html.fromstring(driver.page_source, "lxml")
    except Exception as e:
        log.info(e)
        if tried == 10:
            log.error(f"Can't access url = {url}")
            return None
        else:
            return request_with_retries(driver, url, tried + 1)


def fetch_stores(driver):
    body = request_with_retries(driver, store_url)
    directory_urls = body.xpath(
        '//a[contains(@href, "https://www.nike.com/retail/directory/")]/@href'
    )
    log.info(f"Total countries = {len(directory_urls)}")

    all_directories = []
    store_urls = []
    all_directories = all_directories + directory_urls

    count = 0
    while True:
        new_directories = []
        for directory_url in directory_urls:
            count = count + 1
            body = request_with_retries(driver, directory_url)
            if body is None:
                continue

            stores = body.xpath(
                '//a[contains(@href, "https://www.nike.com/retail/s/")]/@href'
            )
            for store in stores:
                if store not in store_urls:
                    store_urls.append(store)
            directories = body.xpath(
                '//a[contains(@href, "https://www.nike.com/retail/directory/")]/@href'
            )
            for directory in directories:
                if directory not in all_directories:
                    all_directories.append(directory)
                    new_directories.append(directory)
            log.info(
                f"{count}. From {directory_url} : stores = {len(stores)} and directories = {len(directories)} and total stores = {len(store_urls)}"
            )

        log.info(f"Total new directories = {len(new_directories)}")
        if len(new_directories) == 0:
            break
        directory_urls = new_directories

    return store_urls


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
        log.info(f"Address Missing: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_main_section(body, location_name):
    for section in body.xpath("//section"):
        if section.xpath('.//h1[text()="{location_name}"]'):
            return section
    return body


def get_phone(main_section):
    Source = " ".join(main_section.xpath(".//p/text()"))
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(
        r"[\+\(]?[0-9][0-9 .\-\(\)]{8,}[0-9][\(]?[0-9][0-9 .\-\(\)]", Source
    ):
        phone = match
        return phone
    return phone


def get_raw_country(main_section):
    raw_address = ", ".join(
        main_section.xpath(".//div[contains(@class, 'headline-5')]/p/text()")
    )
    if "," not in raw_address:
        return MISSING, MISSING

    address = raw_address.split(",")
    country_code = address[len(address) - 1]
    raw_address = ", ".join(address[0 : len(address) - 1])
    raw_address = " ".join(raw_address.split())
    raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
    if raw_address[len(raw_address) - 1] == ",":
        raw_address = raw_address[:-1]
    raw_address = raw_address.strip()
    country_code = country_code.strip()

    if len(country_code) == 0 or len(raw_address) == 0:
        return MISSING, MISSING
    return raw_address, country_code


def get_lat_lng(main_section):
    link = " ".join(
        main_section.xpath(
            ".//a[contains(@href, 'https://www.google.com/maps/')]/@href"
        )
    )
    if "https://www.google.com/maps/dir/?api=1&destination=" in link:
        link = link.replace("https://www.google.com/maps/dir/?api=1&destination=", "")
        lat, lng = link.split(" ")[0].split(",")
        return lat, lng
    return MISSING, MISSING


def get_hoo(main_section):
    divs = main_section.xpath(".//div")
    for div in divs:
        if len(div.xpath(".//h2[contains(text(), 'Store Hours')]")) > 0:
            return ("; ").join(div.xpath(".//section/text()")).strip()
    return MISSING


def update_location_name(location_name):
    if "nike" in location_name.lower() and "-" in location_name:
        return location_name.split("-")[0].strip()

    if "nike" not in location_name.lower():
        if location_name.upper() == location_name:
            return "NIKE " + location_name
        else:
            return "Nike " + location_name
    return location_name


def fetch_data(driver):
    stores = fetch_stores(driver)
    log.info(f"Total stores = {len(stores)}")
    count = 0
    error_urls = []
    for page_url in stores:
        count = count + 1
        log.info(f"{count}. scrapping store {page_url} ...")
        body = request_with_retries(driver, page_url)
        if body is None:
            error_urls.append(page_url)
            continue

        store_number = MISSING
        location_type = MISSING

        location_name = body.xpath('//h1[contains(@class, "headline-1")]/text()')
        if len(location_name) == 0:
            log.info("Error not found name")
            error_urls.append(page_url)
            continue
        location_name = location_name[0].strip()
        main_section = get_main_section(body, location_name)

        raw_address, country_code = get_raw_country(main_section)
        if country_code == MISSING or main_section == MISSING:
            log.info("Error not found country")
            error_urls.append(page_url)
            continue
        phone = get_phone(main_section)
        latitude, longitude = get_lat_lng(main_section)
        hours_of_operation = get_hoo(main_section)
        street_address, city, state, zip_postal = get_address(raw_address)

        if city == "-02":
            city = "Toco"
        if city == "598-8509":
            city = "泉佐野市"

        location_name = update_location_name(location_name)

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

    log.info(f"Total error urls = {len(error_urls)}")

    count = 0
    for page_url in error_urls:
        count = count + 1
        log.info(f"{count}. scrapping error store {page_url} ...")

        body = request_with_retries(driver, page_url)
        if body is None:
            yield SgRecord(locator_domain=website, page_url=page_url)
            continue

        store_number = MISSING
        location_type = MISSING

        location_name = body.xpath('//h1[contains(@class, "headline-1")]/text()')
        if len(location_name) == 0:
            log.info("Error not found name")
            yield SgRecord(locator_domain=website, page_url=page_url)
            continue
        location_name = location_name[0].strip()
        main_section = get_main_section(body, location_name)

        raw_address, country_code = get_raw_country(main_section)

        phone = get_phone(main_section)
        latitude, longitude = get_lat_lng(main_section)
        hours_of_operation = get_hoo(main_section)
        street_address, city, state, zip_postal = get_address(raw_address)
        location_name = update_location_name(location_name)

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
    CrawlStateSingleton.get_instance().save(override=True)
    log.info(f"Start scrapping {website} ...")
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
