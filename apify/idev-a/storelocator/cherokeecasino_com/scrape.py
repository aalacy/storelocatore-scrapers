from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("cherokeecasino")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://cherokeecasino.com"
    base_url = "https://cherokeecasino.com/"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select_one("footer div.nav-links").select("li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link["href"].replace(":443", "")
            if not page_url.startswith("https"):
                page_url = locator_domain + page_url
            logger.info(page_url)
            driver.get(page_url)
            sp1 = bs(driver.page_source, "lxml")
            block = list(
                sp1.select_one(
                    "div.promo-card-container__floating-card"
                ).stripped_strings
            )[1:-1]
            addr = parse_address_intl(block[2])
            coord = (
                sp1.select_one(
                    "section.promo-card-container .promo-card-container__floating-card"
                )
                .select("a")[-1]["href"]
                .split("destination=")[1]
                .split("%2c")
            )
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=page_url,
                location_name=block[0],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=block[3],
                locator_domain=locator_domain,
                latitude=coord[0],
                longitude=coord[1],
                raw_address=block[2],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
