from lxml import html
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sgselenium.sgselenium import SgChrome
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import ssl


ssl._create_default_https_context = ssl._create_unverified_context

website = "https://www.sugarfina.com"
json_url = f"{website}/rest/V1/storelocator/search/?searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bfield%5D=distance&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bvalue%5D=10000001&searchCriteria%5Bfilter_groups%5D%5B0%5D%5Bfilters%5D%5B6%5D%5Bcondition_type%5D=eq&_=1&searchCriteria%5Bcurrent_page%5D="
store_url = f"{website}/locations"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=website)


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=2, limit=3):
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


def stringify_children_text(body, xpath):
    nodes = body.xpath(xpath + "/text()")
    values = []
    for node in nodes:
        node = node.strip()
        if node:
            values.append(node)
    if len(values) == 0:
        return MISSING
    return (" ".join((" ".join(values)).split())).strip()


def getHoo(data_hoo):
    if data_hoo == MISSING:
        return MISSING
    nodes = html.fromstring("<span>" + data_hoo + "</span>", "lxml")
    hoo = stringify_children(nodes, "//span")
    return hoo


def get_items(driver, page, count=0):
    try:
        driver.get(f"{json_url}{page}")
        random_sleep(driver)
        body = html.fromstring(driver.page_source, "lxml")
        body = body.xpath('//div[contains(@id, "webkit-xml-viewer-source-xml")]')[0]
        body.xpath(".//items")[0]
        return body.xpath(".//item")
    except Exception as e:
        if count == 3:
            log.error(f"{page}. can't able to process e={e}; from url {json_url}{page}")
            return []
        return get_items(driver, page, count + 1)


def fetch_data():
    page = 0
    count = 0
    counts = []

    store_number = MISSING

    with SgChrome() as driver:
        while True:
            page = page + 1
            items = get_items(driver, page)
            log.info(f"Current Page: {page} and Locations: {len(items)}")

            for item in items:
                count = count + 1
                location_name = stringify_children_text(item, ".//name")
                if location_name is MISSING:
                    continue

                page_url = stringify_children_text(item, ".//store_details_link")
                if page_url == MISSING:
                    page_url = store_url
                location_type = stringify_children(item, ".//store_type")
                country_code = stringify_children_text(item, ".//country_id")
                street_address = stringify_children_text(item, ".//street")
                city = stringify_children_text(item, ".//city")
                state = stringify_children_text(item, ".//region")
                zip_postal = stringify_children_text(item, ".//postal_code")
                log.info(f"Location Name: {location_name}, Zip: {zip_postal}")
                phone = stringify_children_text(item, ".//phone")
                latitude = stringify_children_text(item, ".//lat")
                longitude = stringify_children_text(item, ".//lng")
                hours_of_operation = getHoo(stringify_children_text(item, ".//notes"))
                raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                    MISSING, ""
                )
                raw_address = " ".join(raw_address.split())
                raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
                if raw_address[len(raw_address) - 1] == ",":
                    raw_address = raw_address[:-1]

                counts.append(count)

                yield SgRecord(
                    locator_domain="sugarfina.com",
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

            log.debug(f"{page}. total stores = {len(counts)}")
            if len(items) < 9:
                break


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)

    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
