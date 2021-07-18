from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgselenium import SgChrome
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("victrolacoffee")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.victrolacoffee.com"
base_url = "https://www.victrolacoffee.com/pages/locations"


def _p(val):
    return (
        val.replace("Call", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("div.shg-c-lg-6")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.a["href"]
            logger.info(page_url)
            driver.get(page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'shg-c')]//iframe",
                    )
                )
            )
            sp1 = bs(driver.page_source, "lxml")
            try:
                hours = [
                    hh.text.strip().split("(")[0]
                    for hh in sp1.select("div.shg-c p")
                    if hh.text.strip()
                ][1:]
                if "Reserve" in hours[0]:
                    del hours[0]
                phone = ""
                if _p(hours[-1]):
                    phone = hours[-1]
                    del hours[-1]
                if "Open" not in hours[0] and "Monday" not in hours[0]:
                    del hours[0]
                coord = (
                    sp1.select_one("div.shg-c iframe")["src"]
                    .split("!2d")[1]
                    .split("!2m")[0]
                    .split("!3d")
                )
                city = state = zip_postal = ""
                try:
                    driver.switch_to.frame(
                        driver.find_element_by_css_selector("div.shg-c iframe")
                    )
                    addr = (
                        bs(driver.page_source, "lxml")
                        .select_one("div.place-desc-large div.address")
                        .text.strip()
                        .split(",")
                    )
                    city = addr[1].strip()
                    state = addr[2].strip().split(" ")[0].strip()
                    zip_postal = addr[2].strip().split(" ")[1].strip()
                except:
                    addr = json.loads(
                        driver.page_source.split("initEmbed(")[1]
                        .split("}")[0]
                        .strip()[:-2]
                    )[21][3][2]
                    city = addr[1].split(",")[0].strip()
                    state = addr[1].split(",")[1].strip().split(" ")[0].strip()
                    zip_postal = addr[1].split(",")[1].strip().split(" ")[1].strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=link.h1.text.strip(),
                    street_address=addr[0],
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code="US",
                    phone=phone.replace("Call", ""),
                    locator_domain=locator_domain,
                    latitude=coord[1],
                    longitude=coord[0],
                    hours_of_operation="; ".join(hours).replace("–", "-"),
                )
            except:
                import pdb

                pdb.set_trace()


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
