from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from bs4 import BeautifulSoup as bs
import json
import re
from sglogging import SgLogSetup

from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("yha")


locator_domain = "https://www.yha.org.uk"
base_url = "https://www.yha.org.uk/hostels/all-youth-hostels"


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    class_name = "dialog-off-canvas-main-canvas"
    driver = get_driver(base_url, class_name)

    locations = json.loads(
        bs(driver.page_source, "lxml")
        .select_one('script[data-drupal-selector="drupal-settings-json"]')
        .string
    )["mapParagraph"]["24771"]["results"]
    driver.quit()
    logger.info(f"Total stores = {len(locations)}")
    for _ in locations:
        info = bs(_["markup"], "lxml")
        addr = info.select_one("p.location").text.strip().split(",")
        page_url = info.select_one("a.search-teaser__link")["href"]
        if "https" not in page_url:
            page_url = locator_domain + page_url

        logger.info(f"scrapping {page_url} ...")
        class_name2 = "map-with-overlay"

        try:
            driver = get_driver(page_url, class_name2, driver=None)
        except Exception:
            driver = get_driver(page_url, class_name2)

        sp1 = bs(driver.page_source, "lxml")
        _addr = (
            sp1.select_one("div.map-overlay__section a.location")
            .text.strip()
            .split(",")
        )
        hours = ""
        _hr = sp1.find("strong", string=re.compile(r"Hostel opening hours:"))
        if _hr:
            try:
                hours = (
                    list(_hr.find_parent().stripped_strings)[-1]
                    .split("public")[-1]
                    .strip()
                )
            except:
                pass
        phone = ""
        if sp1.find("a", href=re.compile(r"tel:")):
            phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
        if len(addr) > 2:
            street_address = " ".join(_addr[:-3]).replace(addr[-3], "").strip()
            city = addr[-3]
            state = addr[-2]
        else:
            street_address = ""
            city = addr[-2]
            state = ""
        yield SgRecord(
            page_url=page_url,
            location_name=info.h3.text.strip(),
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=addr[-1],
            latitude=_["location"]["lat"],
            longitude=_["location"]["lng"],
            country_code="UK",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours,
            raw_address=", ".join(_addr),
        )
        if driver:
            driver.quit()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
