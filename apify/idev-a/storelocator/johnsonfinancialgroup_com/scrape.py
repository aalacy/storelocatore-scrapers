from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("johnsonfinancialgroup")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.johnsonfinancialgroup.com"
base_url = "https://www.johnsonfinancialgroup.com/locations/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(
            session.get(base_url, headers=_headers).text,
            "lxml",
        )
        locations = soup.select("a.link-arrow")
        for link in locations:
            page_url = link["href"]
            logger.info(page_url)
            sp1 = bs(
                session.get(page_url, headers=_headers).text,
                "lxml",
            )
            _ = json.loads(sp1.find("script", type="application/ld+json").string)
            coord = (
                sp1.select_one("div.container iframe")["src"]
                .split("coord=")[1]
                .split("&amp;")[0]
                .split("&")[0]
                .split(",")
            )
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                country_code=_["address"]["addressCountry"],
                phone=_["telephone"],
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation=_["openingHours"].replace(",", "; "),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
