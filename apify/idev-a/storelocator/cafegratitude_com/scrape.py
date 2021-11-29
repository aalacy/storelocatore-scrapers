from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

logger = SgLogSetup().get_logger("cafegratitude.com")


def _valid(val):
    return val.strip().replace("–", "-")


def fetch_data():
    locator_domain = "https://cafegratitude.com"
    base_url = "https://cafegratitude.com/pages/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.item-locations")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = (
                locator_domain
                + _.find("a", string=re.compile(r"Details", re.IGNORECASE))["href"]
            )
            soup1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(soup1.select_one("div.FeaturedMap__Address p").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                location_name=_.h3.text,
                street_address=addr[0],
                city=addr[-1].split(",")[0].strip(),
                state=addr[-1].split(",")[1].strip().split(" ")[0].strip(),
                zip_postal=addr[-1].split(",")[1].strip().split(" ")[-1].strip(),
                country_code="US",
                phone=soup1.select_one("div.FeaturedMap__Hours a").text,
                locator_domain=locator_domain,
                hours_of_operation=_valid(
                    " ".join(
                        soup1.select("div.FeaturedMap__Hours p")[1].stripped_strings
                    )
                ),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
