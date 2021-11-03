from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("oreck")


def fetch_data():
    locator_domain = "https://oreck.com/"
    base_url = "https://oreck.com/pages/find-your-local-store#store-locator-forms"
    with SgChrome() as driver:
        logger.info(".... initialize ...")
        driver.get(base_url)
        driver.get(base_url)
        logger.info("selecting option")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//select[@id='store-locator-by-radius-store-locator']/option[@value='999999']",
                )
            )
        ).click()
        driver.find_element_by_css_selector("input.store-locator__zip").send_keys(
            "35244", Keys.ENTER
        )
        # wait until locations are loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//ul[@class='exclusive-store-listing']/li[@class='exclusive-store']",
                )
            )
        )
        exclusive_stores = driver.find_elements_by_css_selector(
            "ul.exclusive-store-listing li.exclusive-store"
        )
        logger.info(f"{len(exclusive_stores)} exclusive_stores found")
        for store in exclusive_stores:
            button = store.find_element_by_xpath(".//button")
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)
            sp1 = bs(driver.page_source, "lxml")
            _addr = list(
                sp1.select_one("div.store-details__address div").stripped_strings
            )
            raw_address = " ".join(_addr[1:-1])
            addr = _addr[1:-1]
            street_address = addr[0]
            if street_address.endswith(","):
                street_address = street_address[:-1]
            hours = [
                ":".join(hh.stripped_strings)
                for hh in sp1.select("div.store-details__hours div p")
            ]
            yield SgRecord(
                page_url=base_url,
                location_name=_addr[0],
                street_address=street_address,
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="us",
                phone=_addr[-1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )

        # authorized-store
        authorized_stores = bs(driver.page_source, "lxml").select(
            "ul.authorized-store-listing li.authorized-store"
        )
        logger.info(f"{len(authorized_stores)} authorized_stores found")
        for store in authorized_stores:
            _addr = list(store.stripped_strings)
            addr = _addr[1].split(",")
            yield SgRecord(
                page_url=base_url,
                location_name=_addr[0],
                street_address=" ".join(addr[:-3]),
                city=addr[-3].strip(),
                state=addr[-2].strip(),
                zip_postal=addr[-1].strip(),
                country_code="us",
                phone=_addr[-1],
                locator_domain=locator_domain,
                raw_address=_addr[1],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
