from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

logger = SgLogSetup().get_logger("pricechopper")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://pricechopper.com"
base_url = "https://pricechopper.com/stores"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = soup.select("ul#browse-content a")
        logger.info(f"{len(states)} found")
        for state in states:
            state_url = state["href"]
            cities = bs(session.get(state_url, headers=_headers).text, "lxml").select(
                "ul.map-list a"
            )
            for city in cities:
                city_url = city["href"]
                locations = bs(
                    session.get(city_url, headers=_headers).text, "lxml"
                ).select("ul.map-list li")
                logger.info(
                    f"[{state.text.strip()}] [{city.text.strip()}] {len(locations)}"
                )
                for loc in locations:
                    page_url = loc.a["href"]
                    logger.info(page_url)
                    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    ss = json.loads(
                        sp1.find("script", type="application/ld+json").string
                    )
                    for _ in ss:
                        yield SgRecord(
                            page_url=page_url,
                            store_number=loc["data-lid"],
                            location_name=_["name"],
                            street_address=_["address"]["streetAddress"],
                            city=_["address"]["addressLocality"],
                            state=_["address"]["addressRegion"],
                            zip_postal=_["address"]["postalCode"],
                            country_code="US",
                            phone=_["address"]["telephone"],
                            locator_domain=locator_domain,
                            latitude=_["geo"]["latitude"],
                            longitude=_["geo"]["longitude"],
                            hours_of_operation=_["openingHours"].replace("–", "-"),
                        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
