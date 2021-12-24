from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
import re
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

logger = SgLogSetup().get_logger("yha")

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

locator_domain = "https://www.yha.org.uk"
base_url = "https://www.yha.org.uk/hostels/all-youth-hostels"


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent=user_agent,
        is_headless=True,
    ).driver()


def fetch_data():
    driver = get_driver()
    driver.get(base_url)
    time.sleep(5)
    driver.wait_for_request("/hostels/all-youth-hostels")
    locations = json.loads(
        bs(driver.page_source, "lxml")
        .select_one('script[data-drupal-selector="drupal-settings-json"]')
        .string
    )["mapParagraph"]["24771"]["results"]
    driver.quit()
    for _ in locations:
        info = bs(_["markup"], "lxml")
        addr = info.select_one("p.location").text.strip().split(",")
        page_url = info.select_one("a.search-teaser__link")["href"]
        if "https" not in page_url:
            page_url = locator_domain + page_url
        logger.info(page_url)
        driver = get_driver()
        driver.get(page_url)
        time.sleep(2)
        sp1 = bs(driver.page_source, "lxml")
        _addr = (
            sp1.select_one("div.map-overlay__section a.location")
            .text.strip()
            .split(",")
        )
        phone = ""
        if sp1.find("a", href=re.compile(r"tel:")):
            phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
        if len(addr) > 2:
            street_address = " ".join(_addr[:-3]).replace(addr[-3], "").strip()
            city = addr[-3]
            state = addr[-2]
        else:
            street_address = ""
            city = addr[-2]
            state = ""
        yield SgRecord(
            page_url=page_url,
            location_name=info.h3.text.strip(),
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=addr[-1],
            latitude=_["location"]["lat"],
            longitude=_["location"]["lng"],
            country_code="UK",
            phone=phone,
            locator_domain=locator_domain,
            raw_address=", ".join(_addr),
        )
        driver.quit()


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
