import time
import re
from lxml import html
import random
import ssl
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from sgselenium.sgselenium import SgChrome

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton


ssl._create_default_https_context = ssl._create_unverified_context

website = "https://www.westbrom.co.uk"
branch_page = f"{website}/customer-support/branch-finder"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    response = session.get(url, headers=headers)
    return html.fromstring(response.text, "lxml")


def driver_sleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


def random_sleep(driver, start=5, limit=2):
    driver_sleep(driver, random.randint(start, start + limit))


def fetch_branch(driver, zip_code):
    try:
        input_field = driver.find_element(By.XPATH, "//input[@id='branch_search']")
        input_field.send_keys(str(zip_code))
        input_field.send_keys(Keys.ENTER)
        time.sleep(3)
        input_field.send_keys(Keys.ENTER)
        time.sleep(6)
        driver.find_element(By.ID, "btnBranchSearch").click()
        time.sleep(3)
        log.info("input " + input_field.get_attribute("value"))
        body = html.fromstring(driver.page_source, "lxml")
        urls = body.xpath('//a[contains(text(), "Branch Details")]/@href')
        return urls
    except Exception as e:
        log.error(f"error {e}")
        pass
    return []


def fetch_stores():
    page_urls = []
    zip_codes = [
        "B66 4BL",
        "B65 0DR",
        "B61 8EX",
        "B64 5HE",
        "DY1 1PJ",
        "B42 1TN",
        "DY4 7AY",
        "B21 9LP",
        "B17 9PN",
        "B14 7JZ",
        "B44 9SU",
        "DY6 9JU",
        "B93 0HL",
        "SY16 2LU",
        "B31 2NN",
        "SY11 2SP",
        "B42 1AA",
        "B97 4ET",
        "DY3 1RP",
        "B90 3AH",
        "SY1 1ST",
        "B66 4PB",
        "B66 1DT",
        "B71 3HR",
        "DY8 1DX",
        "B72 1PH",
        "DY4 8EZ",
        "WS1 1JY",
        "B8 2NG",
        "WS10 7AY",
        "SY21 7AD",
        "WV1 3NP",
    ]
    with SgChrome(executable_path=ChromeDriverManager().install()) as driver:
        driver.get(branch_page)
        random_sleep(driver)
        count = 0
        for zip_code in zip_codes:
            count = count + 1
            urls = fetch_branch(driver, zip_code)
            for url in urls:
                if url not in page_urls:
                    page_urls.append(url)
            log.debug(
                f"{count}. from {zip_code} store={len(urls)}, total={len(page_urls)}"
            )

    return page_urls


def stringify_nodes(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.replace("&nbsp;", " ")
            text = text.strip()
            if text:
                values.append(text)
    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def get_lat_lng(nodes=[]):
    if len(nodes) == 0:
        return MISSING, MISSING

    href = nodes[0]
    href = href.replace("https://www.google.co.uk/maps/place/", "")
    if "," not in href:
        return MISSING, MISSING
    parts = href.split(",")
    return parts[0], parts[1]


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
        parts = raw_address.split(",")
        count = len(parts)
        sa = parts[0].strip()
        for index in range(1, count - 2):
            sa = sa + ", " + parts[index].strip()
        return sa, parts[count - 2].strip(), MISSING, parts[count - 1].strip()
    except Exception as e:
        log.info(f"Address Err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    page_urls = fetch_stores()
    log.info(f"Total stores = {len(page_urls)}")
    store_number = MISSING
    location_type = MISSING
    country_code = "UK"
    count = 0
    for page_url in page_urls:
        count = count + 1
        log.debug(f"{count}. scrapping {page_url} ...")
        body = request_with_retries(page_url)
        location_name = body.xpath("//h1/text()")[0]
        raw_address = (
            stringify_nodes(body, '//div[@class="branch-details__location"]')
            .replace("Location", "")
            .strip()
        )
        street_address, city, state, zip_postal = get_address(raw_address)
        phone = get_phone(
            stringify_nodes(body, '//div[@class="branch-details__contact"]')
        )
        latitude, longitude = get_lat_lng(
            body.xpath('//a[contains(@href, "https://www.google.co.uk/maps")]/@href')
        )
        hours_of_operation = (
            stringify_nodes(body, '//table[@class="branch-details__opening-times"]')
            .replace(" (tomorrow)", "")
            .replace(" (today)", "")
        )

        yield SgRecord(
            locator_domain="westbrom.co.uk",
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
    CrawlStateSingleton.get_instance().save(override=False)
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
