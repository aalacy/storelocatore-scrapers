from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
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


logger = SgLogSetup().get_logger("linsgrocery")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://linsgrocery.com"
base_url = "https://www.linsgrocery.com/locations"


def fetch_data():
    with SgRequests() as session:
        with SgChrome() as driver:
            driver.get(base_url)
            sp1 = bs(driver.page_source, "lxml")
            locations = sp1.select("div.locations-map__list > div")
            logger.info(f"{len(locations)} found")
            for _ in locations:
                page_url = locator_domain + _.select_one("a.v-btn")["href"].strip()
                hour_block = _.find("h3", string=re.compile(r"Store Hours"))
                hours = [
                    "".join(hh.stripped_strings)
                    for hh in hour_block.find_next_sibling("div").select("p")
                ]
                addr = list(_.select_one("div.v-card__text p").stripped_strings)
                payload_url = f"https://www.linsgrocery.com/static/locations/{page_url.split('/')[-1]}/payload.js"
                logger.info(payload_url)
                res = session.get(payload_url, headers=_headers).text
                latitude = res.split("latitude:")[1].split("longitude")[0].strip()[:-1]
                longitude = (
                    res.split("longitude:")[1].split("phoneNumber")[0].strip()[:-1]
                )
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.select_one("div.v-card__title").text.strip(),
                    street_address=addr[0],
                    city=addr[1].split(",")[0].strip(),
                    state=addr[1].split(",")[1].strip().split(" ")[0].strip(),
                    zip_postal=addr[1].split(",")[1].strip().split(" ")[-1].strip(),
                    latitude=latitude,
                    longitude=longitude,
                    country_code="US",
                    locator_domain=locator_domain,
                    phone=_.find("a", href=re.compile(r"tel:")).text,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
