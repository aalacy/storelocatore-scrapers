from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://gloriajeanscoffeesbd.com/"
base_url = "https://gloriajeanscoffeesbd.com/"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[@id='find-outlet']",
                )
            )
        )
        locations = driver.find_elements(By.CSS_SELECTOR, "div.slide-content")
        for _ in locations:
            driver.execute_script("arguments[0].click();", _)
            block = bs(driver.page_source, "lxml").select_one(
                "div.outlet-section div.outlet-text"
            )
            addr = block.p.text.replace("-", " ").strip().split()
            phone = ""
            if block.select_one("a.outlet-phone"):
                phone = block.select_one("a.outlet-phone").text.split(":")[-1].strip()
            hours = []
            pp = block.select("p")
            if len(pp) > 1 and "Opening Hours" in pp[1].text:
                hours = list(pp[1].stripped_strings)[1:]
            yield SgRecord(
                page_url=base_url,
                location_name=block.h3.text.strip(),
                street_address=" ".join(addr[:-2]).strip(),
                city=addr[-2].strip(),
                zip_postal=addr[-1].strip(),
                country_code="Bangladesh",
                phone=phone,
                locator_domain=locator_domain,
                raw_address=block.p.text.strip(),
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
