from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from lxml import html
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("actionkarate")


def toggle(driver):
    toggle_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/div[1]/div/div/div/div/div[1]/div[2]/div[1]/div/div/div/div[1]/div/button",
            )
        )
    )
    driver.execute_script("arguments[0].click();", toggle_btn)
    time.sleep(1)


def _close(driver):
    close_retry = 3
    while close_retry:
        close_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//html/body/div[1]/div/div/div/div/div[3]/div/div/div/aside/div[1]/div/button",
                )
            )
        )
        if close_btn:
            break
        close_retry -= 1
    if driver.find_element(
        By.XPATH,
        "//html/body/div[1]/div/div/div/div/div[3]/div/div/div/aside/div[1]/div/button",
    ):
        driver.execute_script("arguments[0].click();", close_btn)
    time.sleep(1)


def fetch_data():
    locator_domain = "https://actionkarate.net/"
    base_url = "https://actionkarate.net/"
    total = 0
    idx = 1
    with SgChrome() as driver:
        driver.get(base_url)
        _close(driver)
        toggle(driver)
        soup = html.fromstring(driver.page_source)
        total = len(
            soup.xpath(
                "//html/body/div[1]/div/div/div/div/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div[2]//button"
            )
        )
        while True:
            if idx > total:
                break
            _close(driver)
            button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f"//html/body/div[1]/div/div/div/div/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div[2]/div[{idx}]//button",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)
            retry_times = 3
            while retry_times:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//div[@class='contact-detail']",
                        )
                    )
                )
                retry_times -= 1

            retry_times = 3
            while retry_times:
                location_name = driver.find_element(By.XPATH, "//h1[1]").text
                retry_times -= 1

            logger.info(f"----------- {location_name}")
            addr = [
                _.text.strip()
                for _ in driver.find_elements(
                    By.XPATH, "//div[@class='contact-detail']/p[2]/span"
                )
                if _.text.strip()
            ]
            phone = driver.find_element(
                By.XPATH, "//div[@class='contact-detail']/p[1]"
            ).text

            yield SgRecord(
                store_number=driver.current_url.split("-")[-1],
                page_url=driver.current_url,
                location_name=location_name,
                street_address=" ".join(addr[:-1])
                .replace(",", "")
                .split("-")[0]
                .strip(),
                city=addr[-1].split(",")[0].strip(),
                state=" ".join(addr[-1].split(",")[1].strip().split(" ")[:-1]),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="us",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=" ".join(addr),
            )
            toggle(driver)

            if idx > total:
                break
            idx += 1


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
