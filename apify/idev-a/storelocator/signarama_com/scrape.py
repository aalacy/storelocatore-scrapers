from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import ssl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import os

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("signarama")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "referer": "https://signarama.com/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://signarama.com"
base_url = "https://signarama.com/location/locator.php"

DEFAULT_PROXY_URL = "https://groups-RESIDENTIAL,country-us:{}@proxy.apify.com:8000/"


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():
        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else DEFAULT_PROXY_URL
        )
        return url.format(proxy_password)
    else:
        return None


def fetch_data():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--proxy-server=%s" % set_proxies())
    if set_proxies():
        _driver = SgChrome(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
            chrome_options=chrome_options,
        )
    else:
        _driver = SgChrome(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
        )
        with _driver as driver:
            driver.get(base_url)
            soup = bs(driver.page_source, "lxml")
            states = soup.select("div.locations a")
            logger.info(f"{len(states)} found")
            for state in states:
                city_url = locator_domain + state["href"]
                driver.get(city_url)
                cities = bs(driver.page_source, "lxml").select(
                    "div.row.mb-5 div.col-lg-3 div.col-5 a"
                )
                logger.info(f"[{len(cities)}] {city_url}")
                for city in cities:
                    page_url = locator_domain + city["href"]
                    if "contact.php" in page_url:
                        continue
                    logger.info(page_url)
                    driver.get(page_url)
                    if driver.current_url != page_url:
                        continue
                    sp1 = bs(driver.page_source, "lxml")
                    _ = json.loads(
                        sp1.find("script", type="application/ld+json")
                        .string.replace("\n", "")
                        .replace("\t", "")
                    )
                    hours = [
                        f"{hh['dayOfWeek']['name']}: {hh['opens']}-{hh['closes']}"
                        for hh in _.get("openingHoursSpecification", [])
                    ]
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_["name"],
                        street_address=_["address"]["streetAddress"].strip(),
                        city=_["address"]["addressLocality"].strip(),
                        state=_["address"]["addressRegion"].strip(),
                        zip_postal=_["address"]["postalCode"].strip(),
                        country_code="US",
                        phone=_.get("telephone"),
                        locator_domain=locator_domain,
                        latitude=_["geo"]["latitude"],
                        longitude=_["geo"]["longitude"],
                        hours_of_operation="; ".join(hours).replace("–", "-"),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
