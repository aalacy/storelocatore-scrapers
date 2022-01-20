import re
import random
import time
from sgpostal.sgpostal import parse_address_intl
from lxml import html
import ssl

from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


import os

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"

website = "https://santamonicaseafood.com"
home_page = "https://smseafoodmarket.com/home/"
contact_page = "https://santamonicaseafood.com/contact"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)


ssl._create_default_https_context = ssl._create_unverified_context

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


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
        log.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetch_data(driver):
    store_number = MISSING
    location_type = MISSING
    latitude = MISSING
    longitude = MISSING
    country_code = "US"

    driver.get(home_page)
    body = html.fromstring(driver.page_source, "lxml")
    random_sleep(driver)
    containers = body.xpath('//div[contains(@class, "vc x-1-2")]')
    log.debug(f"From home page = {len(containers)}")

    for container in containers:
        location_name = stringify_nodes(container, ".//a")
        page_url = container.xpath(".//a/@href")[0]
        address = stringify_nodes(container, ".//p[1]")
        hours_of_operation = stringify_nodes(container, ".//p[2]")
        hours_of_operation = (
            hours_of_operation + " " + stringify_nodes(container, ".//p[3]")
        )

        street_address, city, state, zip_postal = get_address(address)
        phone = get_phone(address)
        phone = phone.replace(zip_postal, "")
        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

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

    driver.get(contact_page)
    random_sleep(driver, 60)
    body = html.fromstring(driver.page_source, "lxml")

    containers = body.xpath('//div[contains(@class, "vc x-1-2")][1]/p/text()')
    log.debug(f"From contact page = {len(containers)}")
    hours_of_operation = MISSING
    page_url = contact_page
    for container in containers:

        location_name = stringify_nodes(container, ".//a")

        street_address, city, state, zip_postal = get_address(address)
        phone = get_phone(address)
        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

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


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgChrome(
        executable_path=ChromeDriverManager().install(),
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
