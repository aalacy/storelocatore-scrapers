from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
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

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

logger = SgLogSetup().get_logger("tommyguns.com")

locator_domain = "https://www.tommyguns.com"
base_url = "https://ca.tommyguns.com/pages/locations"
url = "https://ca.tommyguns.com/blogs/locations"


def fetch_data():
    with SgChrome() as driver:
        with SgRequests() as session:
            driver.get(base_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.location"))
            )
            locations = bs(driver.page_source, "lxml").select("li.location")
            logger.info(f"{len(locations)} found!")
            for _ in locations:
                page_url = (
                    "https://ca.tommyguns.com"
                    + _.select_one("a.location__details")["href"]
                )
                logger.info(page_url)
                soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                hr_text = soup1.select_one("div.store-details__wait-time").text.lower()
                if "coming soon" in hr_text or "hours will be posted" in hr_text:
                    continue
                hours = []
                json_url = f"https://gft.tommyguns.com/api/v1/kiosk/GetShopStatus/{soup1.select_one('div.store-details__wait-time')['data-id']}"
                res = session.get(json_url, headers=_headers)
                if res.status_code == 200:
                    status_data = res.json()["hours"]["openHours"]
                    for day, hh in status_data.items():
                        hours.append(f"{day}: {hh['open_time']} - {hh['close_time']}")

                coord = (
                    _.select_one("a.location__address")["href"]
                    .split("/@")[1]
                    .split(",")
                )
                raw_address = _.address.text.strip()
                addr = parse_address_intl(raw_address + ", Canada")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                city = addr.city
                zip_postal = addr.postcode
                phone = ""
                if _.select_one("a.location__phone--link"):
                    phone = list(
                        _.select_one("a.location__phone--link").stripped_strings
                    )[-1]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.h2.text.strip().replace("–", "-"),
                    street_address=street_address,
                    city=city,
                    state=_.find_parent().find_previous_sibling().text.strip(),
                    zip_postal=zip_postal,
                    latitude=coord[0],
                    longitude=coord[1],
                    country_code="CA",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=raw_address.replace("\n", "").replace("\r", " "),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
