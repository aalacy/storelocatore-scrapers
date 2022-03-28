from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json
from sglogging import SgLogSetup
from sgselenium import SgChrome
import time
import ssl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from tenacity import retry, stop_after_attempt, wait_fixed

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("mkmbs")
locator_domain = "https://www.mkmbs.co.uk/"
base_url = "https://www.mkmbs.co.uk/mobify/proxy/base/"


def _d(page_url, link, addr, hours, phone):
    return SgRecord(
        page_url=page_url,
        location_name=link["name"],
        street_address=" ".join(addr[:-3]),
        city=addr[-3],
        state=addr[-2],
        zip_postal=addr[-1],
        country_code="uk",
        latitude=link["latitude"],
        longitude=link["longitude"],
        phone=link["phone"] or phone,
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
    )


def _h(temp):
    hours = []
    for hh in temp:
        if "open" in hh.lower():
            continue
        hours.append(hh)
    return hours


def _ah(sp1, driver, idx=0):
    addr = []
    hours = []
    phone = ""

    if len(sp1.select("div#address-box")):
        addr = [el.text for el in sp1.select("div#address-box")[idx].select("p")]
        hours = [
            hh.text.strip()
            for hh in sp1.select("div.opening-hours-section")[idx].select("p")
        ]
    if not addr:
        while True:
            time.sleep(2)
            logger.info("-- sleep --")
            if len(driver.find_elements_by_xpath('//div[@id="address-box"]')):
                addr = [
                    el.text
                    for el in driver.find_elements_by_xpath('//div[@id="address-box"]')[
                        idx
                    ].find_elements_by_xpath(".//p")
                ]
                hours = [
                    hh.text.strip()
                    for hh in driver.find_elements_by_xpath(
                        '//div[@class="opening-hours-section"]'
                    )[idx].find_elements_by_xpath(".//p")
                ]
            if addr:
                break

    if sp1.select_one("div#phone-box a"):
        phone = sp1.select_one("div#phone-box a").text.strip()

    return addr, _h(hours), phone


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def get_url(driver=None, url=None):
    if not driver:
        driver = get_driver()
    try:
        driver.get(url)
    except:
        driver = get_driver()
        raise Exception


@retry(wait=wait_fixed(10), stop=stop_after_attempt(5))
def get_url1(driver=None, url=None):
    if not driver:
        driver = get_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@id="address-box"]',
                )
            )
        )
    except:
        driver = get_driver()
        raise Exception


def fetch_data():
    driver = get_driver()
    get_url(driver, base_url)
    links = json.loads(
        bs(driver.page_source, "lxml")
        .select_one("div#mobify_branchdata")
        .text.replace("&quot;", '"')
    )["branch_list"]
    logger.info(f"{len(links)} found")
    for link in links:
        if link["status"] == "pre-live":
            continue
        location_name = link["name"]
        url = "-".join(location_name.split(" ")[1:]).lower()
        page_url = urljoin(
            locator_domain,
            f"branch/{url}",
        )
        logger.info(page_url)
        try:
            get_url1(driver, page_url)
        except:
            continue

        sp1 = bs(driver.page_source, "lxml")
        if sp1.select(".grid-container-desktop"):
            containers = [
                co
                for co in sp1.select(".grid-container-desktop")
                if co.select("div#address-box")
            ]
            for idx, _ in enumerate(containers):
                addr, hours, phone = _ah(sp1, driver, idx)
                yield _d(page_url, link, addr, hours, phone)
        else:
            addr, hours, phone = _ah(sp1, driver)
            yield _d(page_url, link, addr, hours, phone)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
