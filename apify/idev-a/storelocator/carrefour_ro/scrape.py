from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://carrefour.ro"
base_url = "https://carrefour.ro/corporate/magazine"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("app.allStores =")[1]
            .split("app.allCatalogues")[0]
            .strip()[:-1]
        )
        for _ in locations:
            hours_of_operation = ""
            if _["schedule"]:
                hours_of_operation = " ".join(
                    bs(_["schedule"], "lxml").stripped_strings
                )
            page_url = f"https://carrefour.ro/corporate/magazine/{_['city']['slug']}/{_['slug']}"
            if _["type"]:
                location_type = _["type"]["name"]
            else:
                location_type = "Carrefour"
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"]["name"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Romania",
                phone=_["phone"],
                locator_domain=locator_domain,
                location_type=location_type,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
