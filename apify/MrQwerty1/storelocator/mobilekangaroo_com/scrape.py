import ssl
import random
import time
from lxml import html
from xml.etree import ElementTree as ET
from sgpostal.sgpostal import parse_address_intl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://mobilekangaroo.com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=3):
    driver_sleep(driver, random.randint(start, start + limit))


def request_with_retries(url):
    return session.get(url, headers=headers)


def get_XML_root(text):
    return ET.fromstring(text)


def XML_url_pull(url):
    response = request_with_retries(url)
    data = get_XML_root(
        response.text.replace('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', "")
    )
    links = []
    for url in get_XML_object_variable(data, "sitemap", [], True):
        links.append(get_XML_object_variable(url, "loc"))
    return links


def XML_url_pull2(url):
    response = request_with_retries(url)
    data = get_XML_root(
        response.text.replace('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', "")
    )
    links = []
    for url in get_XML_object_variable(data, "url", [], True):
        links.append(get_XML_object_variable(url, "loc"))
    return links


def get_XML_object_variable(Object, varNames, noVal=MISSING, noText=False):
    Object = [Object]
    for varName in varNames.split("."):
        value = []
        for element in Object[0]:
            if varName == element.tag:
                value.append(element)
        if len(value) == 0:
            return noVal
        Object = value

    if noText == True:
        return Object
    if len(Object) == 0 or Object[0].text is None:
        return MISSING
    return Object[0].text


def fetch_stores():
    links = XML_url_pull(f"{website}/sitemap.xml")
    page_urls = []
    for link in links:
        if "locations" in link or "index" in link:
            continue
        links2 = XML_url_pull2(link)
        if len(links2) < 2:
            continue
        links2 = links2[:1]
        page_urls.extend(links2)
    return page_urls


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


def get_raw_lat_lng(arr):
    try:
        if len(arr) == 0:
            return MISSING, MISSING, MISSING
        value = arr[0].split("/@")[1].split(",")
        raw = arr[0].split("/place/")[1].split("/")[0].replace("+", " ")
        return raw, value[0], value[1]
    except:
        return MISSING, MISSING, MISSING


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
    except:
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data(driver):
    page_urls = fetch_stores()
    log.info(f"Total page urls = {len(page_urls)}")

    count = 0
    store_number = MISSING
    location_type = MISSING
    country_code = "US"

    for page_url in page_urls:
        count = count + 1
        log.info(f"{count}. scrapping {page_url} ...")
        driver.get(page_url)
        random_sleep(driver)
        body = html.fromstring(driver.page_source, "lxml")
        location_name = (
            stringify_nodes(body, "//title").replace("Mobile Kangaroo - ", "").strip()
        )
        phone = stringify_nodes(
            body, '//div[contains(@class, "bubble-element Text clickable-element")]'
        )
        raw_address, latitude, longitude = get_raw_lat_lng(
            body.xpath('//a[contains(@href, "maps/place")]/@href')
        )
        hours_of_operation = stringify_nodes(
            body, '//div[contains(text(), ":00") or contains(text(), ":30")]'
        )
        street_address, city, state, zip_postal = get_address(raw_address)

        if latitude == MISSING or longitude == MISSING:
            log.info(f"{count}, missing lat {page_url}")
            continue

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
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgChrome(is_headless=True, driver_wait_timeout=10) as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
