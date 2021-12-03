from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
import re
from selenium.webdriver.support.ui import WebDriverWait
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("carlsjr")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://carlsjr.cl"
base_url = "https://carlsjr.cl/locales/?jsf=jet-engine&pagenum={}"
map_url = "https://www.google.com/maps/search/"


class url_has_at(object):
    """An expectation for checking that an element has a particular css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """

    def __init__(self):
        pass

    def __call__(self, driver):
        if "/@" in driver.current_url and "z/data" in driver.current_url:
            return True
        else:
            return False


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            page = 1
            while True:
                locations = bs(
                    session.get(base_url.format(page), headers=_headers).text, "lxml"
                ).select(
                    "div.jet-listing-grid__item div.jet-engine-listing-overlay-wrap"
                )
                if not locations:
                    break
                page += 1
                for _ in locations:
                    page_url = _.select("a")[-1]["href"]
                    logger.info(page_url)
                    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    info = sp1.select_one(
                        "div#content div.elementor-element-populated div.elementor-element-populated"
                    )
                    raw_address = info.select("div.elementor-element")[3].text.strip()
                    addr = parse_address_intl(raw_address + ", Chile")
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address += " " + addr.street_address_2
                    hours = []
                    _hr1 = info.find("strong", string=re.compile(r"Tienda:"))
                    if _hr1:
                        times = list(_hr1.find_parent().stripped_strings)[-1]
                        if times:
                            hours.append(f"Monday - Saturday: {times}")
                    _hr2 = info.find("strong", string=re.compile(r"Domingo:"))
                    if _hr2:
                        times = list(_hr2.find_parent().stripped_strings)[-1]
                        if times:
                            hours.append(f"Sunday: {times}")
                    driver.get(
                        map_url
                        + sp1.select_one("div.elementor-widget-google_maps").iframe[
                            "src"
                        ]
                    )
                    WebDriverWait(driver, 10).until(url_has_at())
                    coord = (
                        driver.current_url.split("/@")[1].split("/data")[0].split(",")
                    )
                    yield SgRecord(
                        page_url=page_url,
                        location_name=info.h2.text.strip(),
                        street_address=street_address,
                        city=addr.city,
                        state=addr.state,
                        zip_postal=addr.postcode,
                        country_code="Chile",
                        locator_domain=locator_domain,
                        latitude=coord[0],
                        longitude=coord[1],
                        hours_of_operation="; ".join(hours),
                        raw_address=raw_address,
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
