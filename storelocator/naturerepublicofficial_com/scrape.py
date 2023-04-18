from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sglogging import SgLogSetup
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("naturerepublicofficial")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.naturerepublicofficial.com/"
    base_url = "https://www.naturerepublicofficial.com/about-us"
    with SgChrome() as driver:
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[contains(@class, "w-container card-container row")]/div',
                )
            )
        )
        soup = bs(driver.page_source, "lxml")
        locations = soup.select(".w-container.card-container.row > div.w-cell")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            addr = list(_.p.stripped_strings)
            _hr = _.find("span", string=re.compile(r"STORE HOURS"))
            hours = []
            if _hr:
                temp = [
                    hh.text.strip()
                    for hh in _hr.find_next_siblings()
                    if hh.text.strip()
                ]
                for x in range(0, len(temp), 2):
                    if "Call store" in temp[x]:
                        break
                    hours.append(f"{temp[x]} {temp[x+1]}")
            else:
                hours = [_.strong.em.text.strip()]
            yield SgRecord(
                page_url=base_url,
                location_name=_.h4.text.strip(),
                street_address=addr[0],
                city=addr[1].split(",")[0].strip(),
                state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=addr[2],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
