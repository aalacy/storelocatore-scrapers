import random
import time
import re
import ssl
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from sgpostal.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgChrome
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://tfc.com.ng"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)
ssl._create_default_https_context = ssl._create_unverified_context


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=15, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def get_stores(driver):
    driver.get(website)
    random_sleep(driver)
    body = html.fromstring(driver.page_source, "lxml")
    data = body.xpath("//li")
    for item in data:
        if len(item.xpath('.//a[contains(text(), "Locations")]')):
            return item.xpath(".//a/@href")
    return []


def get_lat_lng(url):
    try:
        parts = url.split("@")[1]
        parts = parts.split(",")
        lat = parts[0].strip()
        lng = parts[1].strip()
        if "null" in lat:
            lat = MISSING
        if "null" in lng:
            lng = MISSING
        return lat, lng
    except Exception as e:
        log.info(f"Lat-Lng Error: {e}")
        pass
    return MISSING, MISSING


def stringify_nodes(node):
    values = []
    for text in node.itertext():
        text = text.strip()
        if text:
            values.append(text)
    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def get_phone(texts):
    phone = MISSING
    for Source in texts:
        if Source is None or Source == "":
            continue

        for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
            phone = match
            return phone
    return phone


def click_on_button(driver, body, location_name):
    links = body.xpath("//a/@href")
    for link in links:
        if (
            location_name.lower() in link.lower()
            and "https://www.google.com/maps/place/" in link
        ):
            driver.get(link)
            random_sleep(driver)
            body = html.fromstring(driver.page_source, "lxml")
            texts = []
            for div in body.xpath(
                '//div[contains(@aria-label, "Information for")]/div'
            ):
                texts.append(stringify_nodes(div))
            if len(texts) > 0:
                return texts
    return []


def get_hoo(text):
    parts = text.split()
    index = parts.index("Holiday") - 2
    hoo = (
        " ".join(parts[index : len(parts)])
        .replace(" Holiday hours Hours might differ", ";")
        .replace("Suggest new hours", "")
        .strip()
    )

    hoo = hoo[:-1]
    return hoo


def get_map_data(driver, page_url, retry=1):
    try:
        driver.get(page_url)
        random_sleep(driver)
        body = html.fromstring(driver.page_source, "lxml")
        location_name = stringify_nodes(body.xpath("//h1")[0])

        for frame in driver.find_elements_by_xpath("//iframe"):
            driver.switch_to.frame(frame)
            if "View larger map" in driver.page_source:
                body = html.fromstring(driver.page_source, "lxml")
                map_url = body.xpath('//a[contains(text(), "View larger map")]/@href')[
                    0
                ]

                driver.get(map_url)
                random_sleep(driver)
                body = html.fromstring(driver.page_source, "lxml")
                texts = []
                for div in body.xpath(
                    '//div[contains(@aria-label, "Information for")]/div'
                ):
                    texts.append(stringify_nodes(div))

                if len(texts) == 0:
                    texts = click_on_button(driver, body, location_name)
                if len(texts) > 0:
                    raw_address = texts[0]
                    phone = get_phone(texts)
                    hoo = get_hoo(texts[1])

                    lat, lng = get_lat_lng(driver.current_url)
                    return {
                        "location_name": location_name,
                        "raw_address": raw_address,
                        "phone": phone,
                        "hoo": hoo,
                        "lat": lat,
                        "lng": lng,
                    }
    except Exception as e:
        log.info(f"{page_url} error: {e}")
        pass

    if retry > 6:
        return None
    log.debug(f"{retry} retrying ...")
    return get_map_data(driver, page_url, retry + 1)


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
        log.info(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data(driver):
    page_urls = get_stores(driver)

    log.info(f"Total stores = {len(page_urls)}")
    count = 0
    for page_url in page_urls:
        count = count + 1
        log.debug(f"{count}. scrapping {page_url}")
        data = get_map_data(driver, page_url)
        if data == None:
            continue

        street_address, city, state, zip_postal = get_address(data["raw_address"])
        yield SgRecord(
            locator_domain=website,
            store_number=MISSING,
            location_type=MISSING,
            page_url=page_url,
            location_name=data["location_name"],
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code="NG",
            phone=data["phone"],
            latitude=data["lat"],
            longitude=data["lng"],
            hours_of_operation=data["hoo"],
            raw_address=data["raw_address"],
        )
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
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
