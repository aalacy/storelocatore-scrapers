from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from lxml import html
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
    with SgChrome() as driver:
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
            if idx > total:
                break
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
            time.sleep(1)
            location_name = driver.find_element_by_xpath("//h1[1]").text
            addr = [
                _.text
                for _ in driver.find_elements_by_xpath(
                    "//div[@class='contact-detail']/p[2]/span"
                )
            ]
            phone = driver.find_element_by_xpath(
                "//div[@class='contact-detail']/p[1]"
            ).text

            yield SgRecord(
                store_number=driver.current_url.split("-")[-1],
                page_url=driver.current_url,
                location_name=location_name,
                street_address=addr[0].replace(",", ""),
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
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
