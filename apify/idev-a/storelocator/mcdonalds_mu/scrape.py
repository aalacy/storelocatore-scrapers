from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mcdonalds")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.mu/"
base_url = "https://mcdonalds.mu/our-location"


def _v(val):
    return val.replace("#", "'").strip()


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.featurecallout div.mcd-feature-callout__card"
        )
        for loc in locations:
            page_url = locator_domain + loc.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            _ = json.loads(sp1.find("script", type="application/ld+json").string)
            hours = []
            for hh in _["openingHoursSpecification"]:
                hours.append(
                    f"{', '.join(hh['dayOfWeek'])}: {hh['opens']} - {hh['closes']}"
                )
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                zip_postal=_["address"]["postalCode"],
                latitude=_["geo"]["latitude"],
                longitude=_["geo"]["longitude"],
                country_code="Mauritius",
                phone=_["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
