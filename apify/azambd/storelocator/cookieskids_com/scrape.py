from sgpostal.sgpostal import parse_address_intl
import random
import time
import json
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

DOMAIN = "cookieskids.com"
website = "https://www.cookieskids.com"
page_url = f"{website}/locations.aspx"
MISSING = SgRecord.MISSING
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def get_markers(response, noVal=MISSING):
    try:
        part1 = response.split("markers = ")[1]
        part2 = part1.split("map = ")[0].strip()
        return json.loads(part2[:-1].replace("'", '"'))
    except Exception as e:
        log.info(f"Lat/lng missing: {e}")
        return []


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
    driver.get(page_url)
    random_sleep(driver)
    response = driver.page_source
    body = html.fromstring(response, "lxml")
    columns = body.xpath('//div[contains(@class, "large-5")]/div')

    markers = get_markers(response)

    for column in columns:
        hours_of_operation = column.xpath(
            './/div[contains(@class, "sl-hours-heading")]/text()'
        )[0]
        for info in column.xpath('.//div[contains(@class, "sl-info")]'):
            store_number = MISSING
            location_type = MISSING

            location_name = info.xpath(".//strong/text()")[0].strip()
            divTexts = info.xpath(".//div/text()")
            raw_address = divTexts[0].strip() + " " + divTexts[1].strip()
            phone = divTexts[2].strip()
            latitude = MISSING
            longitude = MISSING
            country_code = "US"

            for marker in markers:
                if marker[0].lower() in raw_address.lower():
                    latitude = str(marker[1])
                    longitude = str(marker[2])

            street_address, city, state, zip_postal = get_address(raw_address)
            if city == MISSING:
                city = raw_address.split(",")[0].split(" ")[-1]

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


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgChrome(user_agent=user_agent) as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
