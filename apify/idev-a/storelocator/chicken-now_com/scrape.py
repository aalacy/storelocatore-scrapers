from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import SgLogSetup
from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt, wait_fixed
import time


logger = SgLogSetup().get_logger("")
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "http://chicken-now.com"
base_url = "http://chicken-now.com/locations.html"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


@retry(wait=wait_fixed(2), stop=stop_after_attempt(2))
def get_url(driver=None, url=None):
    if not driver:
        driver = get_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'button[data-item-id="address"]',
                )
            )
        )
    except:
        driver = get_driver()
        raise Exception


def _hoo(sp1, hours):
    for hh in sp1.select("div#pane table")[0].select("tr"):
        td = hh.select("td")
        hours.append(f"{td[0].div.text.strip()}: {td[1]['aria-label'].split(',')[0]}")


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    soup = bs(driver.page_source, "lxml")
    locations = soup.select("div#locations a")
    for _ in locations:
        page_url = _["href"]
        logger.info(page_url)
        try:
            get_url(driver, page_url)
        except:
            continue

        sp1 = bs(driver.page_source, "lxml")
        try:
            raw_address = sp1.select_one('button[data-item-id="address"]')[
                "aria-label"
            ].split(":")[-1]
        except:
            continue
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        info = _.text.split("/")
        phone = ""
        if sp1.select_one('button[data-tooltip="Copy phone number"]'):
            phone = sp1.select_one('button[data-tooltip="Copy phone number"]')[
                "data-item-id"
            ].split(":")[-1]
        try:
            coord = driver.current_url.split("/@")[1].split("/data")[0].split(",")
        except:
            coord = ["", ""]
        hours = []
        if len(sp1.select("div#pane table")) > 1:
            _hoo(sp1, hours)
        else:
            _hr = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="oh"]')
            driver.execute_script("arguments[0].click();", _hr)
            time.sleep(3)
            sp1 = bs(driver.page_source, "lxml")
            _hoo(sp1, hours)

        state = info[1].split(",")[-1].strip()
        country_code = "US"
        if state == "Puerto Rico":
            country_code = "Puerto Rico"
            state = ""
        yield SgRecord(
            page_url=page_url,
            location_name=info[0],
            street_address=street_address,
            city=info[1].split(",")[0].strip(),
            state=state,
            zip_postal=addr.postcode,
            country_code=country_code,
            phone=phone,
            latitude=coord[0],
            longitude=coord[1],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=raw_address,
        )

    if driver:
        driver.close()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
