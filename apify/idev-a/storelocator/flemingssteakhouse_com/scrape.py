from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from sgrequests import SgRequests
import re
from sglogging import SgLogSetup
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

logger = SgLogSetup().get_logger("flemingssteakhouse")

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    with SgChrome() as driver:
        locator_domain = "https://www.flemingssteakhouse.com/"
        base_url = "https://www.flemingssteakhouse.com/locations/"
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        links = soup.select("ul.locations li a")
        logger.info(f"{len(links)} locations found")
        with SgRequests() as session:
            cookies = []
            for cookie in driver.get_cookies():
                cookies.append(f"{cookie['name']}={cookie['value']}")
            _headers["cookie"] = "; ".join(cookies)
            for link in links:
                logger.info(link["href"])
                soup1 = bs(session.get(link["href"], headers=_headers).text, "lxml")
                block = soup1.find("p", string=re.compile(r"^Address", re.IGNORECASE))
                _content = list(block.find_next_sibling().stripped_strings)
                phone = _content[-1]
                del _content[-1]
                _hr = soup1.find("p", string=re.compile(r"^Hours"))
                hours = []
                for hh in list(_hr.find_next_sibling("p").stripped_strings):
                    if hh == "Curbside Pickup":
                        break
                    if "Dining" in hh:
                        continue
                    hours.append(hh)

                yield SgRecord(
                    page_url=link["href"],
                    location_name=soup1.h1.text.strip().replace("’", "'"),
                    street_address=_content[0],
                    city=_content[1].split(",")[0].strip(),
                    state=_content[1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=_content[1].split(",")[1].strip().split(" ")[-1].strip(),
                    country_code="US",
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=_valid("; ".join(hours)),
                    raw_address=" ".join(_content),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
