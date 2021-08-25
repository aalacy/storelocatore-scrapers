from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgSelenium
import ssl
from selenium.common.exceptions import TimeoutException

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "surgefun.com"
BASE_URL = "https://surgefun.com"
LOCATION_URL = "https://surgefun.com/locations/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def scroll_until_loaded(driver):
    check_height = driver.execute_script("return document.body.scrollHeight;")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(driver, 2).until(
                lambda driver: driver.execute_script(
                    "return document.body.scrollHeight;"
                )
                > check_height
            )
            check_height = driver.execute_script("return document.body.scrollHeight;")
        except TimeoutException:
            break


def load_data(driver, page_url, count, load=False):
    if load:
        driver.get(page_url)
    driver.find_element_by_xpath("/html/body/div[2]/div/div/section[2]").click()
    scroll_until_loaded(driver)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div#locInfo > div.container")
            )
        )
    except TimeoutException:
        if count < 15:
            count += 1
            load_data(driver, page_url, count, True)
            log.info("Website load not complete, Try to reload")
        else:
            pass
    return driver


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_urls = (
        soup.find("main", {"class": "site-main"})
        .find("div", {"class": "elementor-column-wrap elementor-element-populated"})
        .find_all(
            "a", {"class": "elementor-button-link elementor-button elementor-size-sm"}
        )
    )
    driver = SgSelenium(is_headless=True).chrome()
    for row in store_urls:
        page_url = row["href"]
        driver.get(page_url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "locInfo"))
        )
        try:
            driver.find_element_by_xpath("//h2[text()='COMING SOON!']")
            continue
        except:
            pass
        driver = load_data(driver, page_url, 0, False)
        content = driver.find_element_by_id("locInfo")
        location_name = content.find_element_by_css_selector(
            "div.col-md-4.text-left > h4"
        ).text.strip()
        address = (
            content.find_element_by_css_selector("div.col-md-4.text-left > p")
            .text.replace("\n", ",")
            .split(",")
        )
        if len(address) > 4:
            street_address = (address[0] + "," + address[1]).strip()
            city = address[2].strip()
            state_zip = address[3].strip().split()
            state = state_zip[0].strip()
            zip_code = state_zip[1].strip()
            phone = address[4].strip()
        else:
            street_address = address[0].strip()
            city = address[1].strip()
            state_zip = address[2].strip().split()
            state = state_zip[0].strip()
            zip_code = state_zip[1].strip()
            phone = address[3].strip()
        hours_of_operation = ", ".join(
            content.find_element_by_css_selector("div.col-md-3.text-left")
            .text.replace("Business Hours\n", "")
            .split("\n")
        )
        store_number = MISSING
        country_code = "US"
        location_type = "surgefun"
        latitude = MISSING
        longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_code.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address}, {city}, {state} {zip_code} ",
        )
    driver.quit()


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
