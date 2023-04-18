from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

logger = SgLogSetup().get_logger("specsavers")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://en.specsavers.es"
base_url = "https://en.specsavers.es/stores"


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        with SgRequests() as session:
            driver.get(base_url)
            cookies = []
            for cookie in driver.get_cookies():
                cookies.append(f"{cookie['name']}={cookie['value']}")
            _headers["cookie"] = "; ".join(cookies)
            soup = bs(driver.page_source, "lxml")
            locations = soup.select(
                "div.stores-content-block div.field-name-field-content-body p a"
            )
            for link in locations:
                page_url = link["href"]
                if not page_url.startswith("http"):
                    page_url = locator_domain + page_url
                logger.info(page_url)
                res = session.get(page_url, headers=_headers).text
                coord = json.loads(res.split("var position =")[1].split(";")[0].strip())
                sp1 = bs(res, "lxml")
                addr = (
                    " ".join(list(sp1.select_one("div.store p").stripped_strings))
                    .replace("\n", "")
                    .split(",")
                )
                street_address = city = state = ""
                state = addr[-2].strip()
                idx = -3
                if state == "Orihuela Costa":
                    state = ""
                    idx += 1

                city = addr[idx].strip()
                street_address = ", ".join(addr[:idx]).strip()

                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in sp1.select("table.opening--day-and-time tr")
                ]
                phone = ""
                if sp1.select_one("a.contact--store-telephone"):
                    phone = sp1.select_one("a.contact--store-telephone").text.strip()
                yield SgRecord(
                    page_url=page_url,
                    location_name=sp1.h1.text.strip(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=addr[-1].split()[-1],
                    country_code="Spain",
                    phone=phone,
                    latitude=coord["lat"],
                    longitude=coord["lng"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=", ".join(addr).strip(),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
