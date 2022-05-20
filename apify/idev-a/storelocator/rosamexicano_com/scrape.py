from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rosamexicano")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.rosamexicano.com/"
base_url = "https://www.rosamexicano.com/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find("script", type="application/ld+json")
            .string.strip()
        )
        for _ in locations["subOrganization"]:
            logger.info(_["url"])
            sp1 = bs(session.get(_["url"], headers=_headers).text, "lxml")
            _hr = sp1.find("strong", string=re.compile(r"Hours of Operation"))
            hours = ""
            if _hr:
                hours = _hr.find_next_sibling("strong").text.strip()
            if not hours:
                hours = sp1.select_one("section#intro strong").text
                if "AM" not in hours:
                    hours = ""
            coord = (
                sp1.select_one("div.gmaps")["data-gmaps-static-url-mobile"]
                .split("&center=")[1]
                .split("&")[0]
                .split("%2C")
            )
            yield SgRecord(
                page_url=_["url"],
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                location_type=_["@type"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                latitude=coord[0],
                longitude=coord[1],
                country_code="US",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
