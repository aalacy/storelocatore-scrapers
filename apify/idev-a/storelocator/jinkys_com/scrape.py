from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgselenium import SgFirefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import json
import re

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
    with SgFirefox(executable_path=r"/mnt/g/work/mia/geckodriver.exe") as driver:
        locator_domain = "https://www.jinkys.com/"
        base_url = "https://www.jinkys.com/"
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='locations']"))
        )
        soup = bs(driver.page_source, "lxml")
        locations = json.loads(
            soup.select_one("script.js-react-on-rails-component").string.strip()
        )
        for _ in locations["preloadQueries"][0]["data"]["restaurant"]["homePage"][
            "sections"
        ][-1]["locations"]:
            hours_of_operation = "; ".join(_["schemaHours"])
            if _["openingRanges"][0]["additionalHoursContent"] is not None:
                if re.search(
                    r"closed temporarily",
                    _["openingRanges"][0]["additionalHoursContent"],
                    re.IGNORECASE,
                ):
                    hours_of_operation = "Temporarily Closed"
                if re.search(
                    r"temporary state shut down",
                    _["openingRanges"][0]["additionalHoursContent"],
                    re.IGNORECASE,
                ):
                    hours_of_operation = "Temporarily Closed"
            page_url = ""
            try:
                page_url = _["socialHandles"][0]["url"]
            except:
                pass
            yield SgRecord(
                page_url=page_url,
                store_number=_["restaurantId"],
                location_name=_["name"],
                street_address=_["streetAddress"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postalCode"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
