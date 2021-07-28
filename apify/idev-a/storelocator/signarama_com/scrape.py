from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import ssl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

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


def _d(city, page_url):
    addr = list(city.select("p.m-0")[-1].stripped_strings)
    return SgRecord(
        page_url=page_url,
        location_name=city.strong.text.strip(),
        street_address=" ".join(addr[:-1]),
        city=addr[-1].split(",")[0].strip(),
        state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
        zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
        country_code="US",
        phone=city.select_one("a.text-red").text.strip(),
        locator_domain=locator_domain,
    )


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        states = soup.select("div.locations a")
        logger.info(f"{len(states)} found")
        for state in states:
            city_url = locator_domain + state["href"]
            driver.get(city_url)
            cities = bs(driver.page_source, "lxml").select(
                "div.row.mb-5 div.col-lg-3 div.col-7"
            )
            logger.info(f"[{len(cities)}] {city_url}")
            for city in cities:
                page_url = locator_domain + city.a["href"]
                logger.info(page_url)
                if "contact.php" in page_url:
                    yield _d(city, page_url)
                else:
                    try:
                        driver.get(page_url)
                    except:
                        driver.get(page_url)

                    if driver.current_url != page_url:
                        yield _d(city, page_url)
                    else:
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
