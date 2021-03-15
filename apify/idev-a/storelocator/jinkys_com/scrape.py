from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgselenium import SgFirefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import json

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "Host": "www.jinkys.com",
    "Connection": "keep-alive",
    "upgrade-insecure-requests": "1",
    "Cache-Control": "no-cache",
    "TE": "Trailers",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
}


def fetch_data():
    with SgFirefox() as driver:
        locator_domain = "https://www.jinkys.com/"
        base_url = "https://www.jinkys.com/"
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='locations']"))
        )
        soup = bs(driver.page_source, "lxml")
        locations = soup.findAll("script", type="application/ld+json")
        for location in locations:
            _ = json.loads(location.string.strip())
            yield SgRecord(
                page_url=_["url"],
                location_name=_["address"]["addressLocality"],
                location_type=_["@type"],
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                country_code="US",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(_["openingHours"]),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
