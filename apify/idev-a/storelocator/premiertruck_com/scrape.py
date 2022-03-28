from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from tenacity import retry, stop_after_attempt, wait_fixed
from webdriver_manager.chrome import ChromeDriverManager
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("premiertruck")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.premiertruck.com"
base_url = "https://images.ebizautos.media/fonts/dealerlocator/sites/12153/data/locations.json?v=2&formattedAddress=&boundsNorthEast=&boundsSouthWest="

ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


def get_driver():
    return SgChrome(
        executable_path=ChromeDriverManager().install(),
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ).driver()


@retry(wait=wait_fixed(2), stop=stop_after_attempt(2))
def get_url(driver=None, url=None):
    if not driver:
        driver = get_driver()
    try:
        driver.get(url)
    except:
        driver = get_driver()
        raise Exception


def fetch_data():
    driver = get_driver()
    with SgRequests(proxy_country="us") as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            page_url = locator_domain + _["web"]
            logger.info(page_url)
            get_url(driver, page_url)
            sp1 = bs(driver.page_source, "lxml")
            hours = []
            days = list(
                sp1.select_one("div#section-hours table thead tr").stripped_strings
            )
            times = sp1.select("div#section-hours table tbody tr")[0].select("td")[1:]
            for x in range(len(days)):
                hours.append(f"{days[x]}: {' '.join(times[x].stripped_strings)}")

            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]

            country_code = "US"
            if _["state"] in ca_provinces_codes:
                country_code = "CA"
            phone = _["phone"]
            if not phone and sp1.find("a", href=re.compile(r"tel:")):
                phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal"].replace("Canada", "").strip(),
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
