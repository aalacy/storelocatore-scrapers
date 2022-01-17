from sgpostal.sgpostal import parse_address_intl
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
        if location_name != MISSING:
            return body
        log.debug("Error getting page")

    except Exception as e:
        log.debug(f"Error getting page with e={e}")
    if count == 4:
        return None
    return get_response(driver, url, count + 1)


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


def get_hoo(body):
    result = body.xpath('//div[@class="detail_results"]')
    foundDays = []
    hoo = []
    for day in result:
        data = stringify_children(day, ".//p")
        dayName = data.split()[0]
        if dayName in foundDays:
            continue
        foundDays.append(dayName)
        hoo.append(data)
    return " ".join(hoo)


def get_store(driver, page_url, retry=1):
    body = get_response(driver, page_url)
    if body is None:
        if retry == 4:
            return None
        log.error("Can't get response")
        return get_store(driver, page_url, retry + 1)

    location_name = stringify_children(body, "//h1/span")
    phone = stringify_children(body, '//span[@itemprop="telephone"]')
    street_address = stringify_children(body, '//span[@itemprop="streetAddress"]')
    city = stringify_children(body, '//span[@itemprop="addressLocality"]')
    state = stringify_children(body, '//span[@itemprop="addressRegion"]')
    zip_postal = stringify_children(body, '//span[@itemprop="postalCode"]')
    latitude = body.xpath('//span[@property="latitude"]/@content')
    longitude = body.xpath('//span[@property="longitude"]/@content')
    hours_of_operation = get_hoo(body)
    raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(MISSING, "")
    raw_address = " ".join(raw_address.split())
    raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
    if raw_address[len(raw_address) - 1] == ",":
        raw_address = raw_address[:-1]

    if len(latitude) > 0:
        latitude = latitude[0]
    else:
        latitude = "0.0"
        log.debug("No latitude found")
        if retry != 4:
            return get_store(driver, page_url, retry + 1)

    if len(longitude) > 0:
        longitude = longitude[0]
    else:
        longitude = "0.0"
        log.debug("No longitude found")
        if retry != 4:
            return get_store(driver, page_url, retry + 1)

    street_address1, city1, state1, zip_postal1 = get_address(raw_address)
    if street_address1 != street_address:
        street_address = street_address1
        log.debug(
            f"Separate address: {street_address}, {street_address1}, {city1}, {state1}, {zip_postal1}"
        )

    return {
        "location_name": location_name,
        "phone": phone,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip_postal": zip_postal,
        "latitude": latitude,
        "longitude": longitude,
        "hours_of_operation": hours_of_operation,
        "raw_address": raw_address,
    }


def fetch_data():
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(json_url)
        random_sleep(driver)
        body = html.fromstring(driver.page_source, "lxml")
        page_urls = body.xpath('//span[contains(text(), "/store-detail/")]/text()')
        log.debug(f"Total stores = {len(page_urls)}")

        count = 0

        store_number = MISSING
        location_type = MISSING
        country_code = "AU"

        for page_url in page_urls:
            count = count + 1
            log.debug(f"{count}. scrapping {page_url} ...")

            store = get_store(driver, page_url)
            if store is None:
                log.error("Can't get response")
                continue

            location_name = store["location_name"]
            phone = store["phone"]
            street_address = store["street_address"]
            city = store["city"]
            state = store["state"]
            zip_postal = store["zip_postal"]
            latitude = store["latitude"]
            longitude = store["longitude"]
            hours_of_operation = store["hours_of_operation"]
            raw_address = store["raw_address"]

            if latitude.startswith("0.0") or longitude.startswith("0.0"):
                latitude = MISSING
                longitude = MISSING

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
    CrawlStateSingleton.get_instance().save(override=False)
    scrape()
