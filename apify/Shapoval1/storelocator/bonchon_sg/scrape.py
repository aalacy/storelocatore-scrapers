from sgpostal.sgpostal import parse_address_intl
import random
import ssl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from lxml import html
import re
import time
import json

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

ssl._create_default_https_context = ssl._create_unverified_context

website = "https://bonchon.sg"
page_url = f"{website}/#post-28/"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
session = SgRequests()
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


def random_sleep(driver, start=9, limit=5):
    driver_sleep(driver, random.randint(start, start + limit))


def get_JS_object(response, varName, noVal=MISSING):
    JSObject = re.findall(f'{varName} = "(.+?)";', response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


def get_google_parent(data, depth=7, string=""):
    count = 0
    while True:
        result = None
        for singleData in data:
            if string in json.dumps(singleData):
                result = singleData
                break
        if result is None:
            return None
        data = singleData
        count = count + 1
        if count == depth:
            return singleData


def get_information_from_google(url):
    response = request_with_retries(url)
    data = (
        get_JS_object(response.text, "_pageData")
        .replace("null", '"null"')
        .replace('\\"', '"')
        .replace('\\"', '"')
    )
    data = json.loads(data)

    rootJsons = get_google_parent(data, 2, '"name"')
    locations = []

    for rootJson in rootJsons:
        dataJSONs = get_google_parent(rootJson, 4, '"name"')

        for dataJSON in dataJSONs:
            latitude = dataJSON[1][0][0][0]
            longitude = dataJSON[1][0][0][1]

            name_part = get_google_parent(dataJSON, 2, '"name"')
            location_name = name_part[1][0]
            location_name = (
                location_name.replace("\\u0026", "&")
                .replace("\\n", " ")
                .replace("\n", " ")
                .strip()
            )

            locations.append(
                {
                    "location_name": location_name,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )

    return locations


def fetch_stores():
    response = request_with_retries(page_url)
    body = html.fromstring(response.text, "lxml")

    googleUrl = body.xpath(
        '//iframe[contains(@data-src, "google.com/maps")]/@data-src'
    )[0]

    return get_information_from_google(googleUrl), googleUrl


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


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        parts = phone.split(" ")
        phone = []
        for part in parts:
            if "." not in part:
                phone.append(part)
        return " ".join(phone)
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
        log.info(f"Address Error: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data(driver):
    stores, googleUrl = fetch_stores()

    log.info(f"Total stores = {len(stores)}")
    driver.get(googleUrl)
    random_sleep(driver, 40)
    store_markers = []

    for frame in driver.find_elements(By.XPATH, "//iframe"):

        try:

            main = driver.find_element(
                By.XPATH,
                '//div[contains(@style, "https://maps.gstatic.com/mapfiles/openhand_8_8.cur")]',
            )

            store_markers = main.find_elements(
                By.XPATH, './/div[contains(@role, "button")]'
            )
            if len(store_markers) >= len(stores):
                break
        except Exception as e:
            log.info(f"maps.gstatic.com Error: {e}")
            pass
    log.info(f"total store_markers = {len(store_markers)}")

    names = []
    store_number = MISSING
    location_type = MISSING
    hours_of_operation = MISSING
    country_code = "SG"

    count = 0
    for store_marker in store_markers:
        count = count + 1
        try:
            log.debug(f"{count}. click on location ...")
            driver.execute_script("arguments[0].click();", store_marker)
            random_sleep(driver, 20)
            body = html.fromstring(driver.page_source, "lxml")
            text = stringify_nodes(body, '//div[@id="featurecardPanel"]')

            log.info(text)

            for store in stores:
                location_name = store["location_name"]
                if location_name in text:
                    if location_name in names:
                        continue
                    names.append(location_name)

                    latitude = store["latitude"]
                    longitude = store["longitude"]

                    phone = get_phone(text)
                    addresstext = (
                        text.split("Maps")[1]
                        .split("bonchon.sg")[0]
                        .replace(phone, "")
                        .replace("View in Google", "")
                    )

                    log.info(f"Address::: {addresstext.strip()}")
                    street_address, city, state, zip_postal = get_address(addresstext)

                    raw_address = (
                        f"{street_address} {city} {state} {zip_postal}".replace(
                            MISSING, ""
                        )
                    )

                    yield SgRecord(
                        locator_domain="bonchon.sg",
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
        except Exception as e:
            log.info(f"Failed###: {store_marker}, err:{e}")
            continue


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgChrome(is_headless=True, user_agent=user_agent) as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
