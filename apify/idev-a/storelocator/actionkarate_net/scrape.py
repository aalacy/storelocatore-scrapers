from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox
from lxml import html
from sgscrape.sgpostal import parse_address_intl
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time


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


def _close(driver, close_btn):
    if driver.find_element_by_xpath(
        "//html/body/div[1]/div/div/div/div/div[3]/div/div/div/aside/div[1]/div/button"
    ):
        driver.execute_script("arguments[0].click();", close_btn)
        time.sleep(1)


def fetch_data():
    locator_domain = "https://actionkarate.net/"
    base_url = "https://actionkarate.net/"
    total = 0
    idx = 1
    with SgFirefox(executable_path=r"/mnt/g/work/mia/geckodriver.exe") as driver:
        driver.get(base_url)
        close_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//html/body/div[1]/div/div/div/div/div[3]/div/div/div/aside/div[1]/div/button",
                )
            )
        )
        _close(driver, close_btn)
        toggle(driver)
        soup = html.fromstring(driver.page_source)
        total = len(
            soup.xpath(
                "//html/body/div[1]/div/div/div/div/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div[2]//button"
            )
        )
        while True:
            _close(driver, close_btn)
            button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f"//html/body/div[1]/div/div/div/div/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div[2]/div[{idx}]//button",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", button)
            block = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//html/body/div[1]/div/div/div/div/div[2]/div[2]/div[1]/div/div/div",
                    )
                )
            )
            location_name = driver.find_element_by_xpath("//h1[1]").text
            addr = parse_address_intl(block.text.split("\n")[0])
            phone = block.text.split("\n")[1]

            yield SgRecord(
                store_number=driver.current_url.split("-")[-1],
                page_url=driver.current_url,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="us",
                phone=phone,
                locator_domain=locator_domain,
            )
            toggle(driver)

            if idx > total:
                break
            idx += 1


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
