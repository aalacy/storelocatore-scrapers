from sgpostal.sgpostal import parse_address_intl
import re
from lxml import html
import time
import random

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "applebees.com"
website = "https://www.applebees.com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except:
        pass


def random_sleep(driver, start=5, limit=6):
    driver_sleep(driver, random.randint(start, start + limit))


def get_text_from_nodes(body, xpath):
    text = ""
    for node in body.xpath(xpath):
        text = text + " ".join(node.itertext())

    text = text.strip().replace("\n", " ").replace("\r", " ").replace("\t", " ")
    text = text.strip()
    return " ".join(text.split())


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


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


def fetch_data(driver):
    page_url = f"{website}/en/opportunities/international/international-locations"
    driver.get(page_url)
    random_sleep(driver, 60)

    body = html.fromstring(driver.page_source, "lxml")

    countries = body.xpath('//div[contains(@class, "franchise__container")]/h2/text()')

    uls = body.xpath(
        '//div[contains(@class, "franchise__container")]/ul[contains(@class, "row")]'
    )
    if len(uls) + 1 == len(countries):
        countries[len(countries) - 2] = countries[len(countries) - 1]

    count = 0
    for index in range(0, len(uls)):
        country = countries[index]
        stores = uls[index].xpath(".//li")
        countryCount = 0
        for store in stores:
            count = count + 1
            countryCount = countryCount + 1
            store_number = MISSING
            location_type = MISSING
            latitude = MISSING
            longitude = MISSING
            hours_of_operation = MISSING

            location_name = get_text_from_nodes(store, ".//h3")
            log.info(f"Location Name: {location_name}")
            if location_name == "":
                continue
            phone = get_phone(get_text_from_nodes(store, ".//p"))
            raw_address = get_text_from_nodes(store, ".//address")

            street_address, city, state, zip_postal = get_address(raw_address)
            country_code = country

            yield SgRecord(
                locator_domain=DOMAIN,
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
        log.debug(f"{index + 1}. {country} stores = {countryCount}")
    log.debug(f"Total Stores = {count}")
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()

    with SgChrome(
        is_headless=True,
        user_agent=user_agent,
    ) as driver:
        with SgWriter(
            SgRecordDeduper(
                SgRecordID(
                    {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
                )
            )
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
