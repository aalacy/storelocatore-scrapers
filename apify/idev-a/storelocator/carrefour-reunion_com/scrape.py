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

locator_domain = "https://www.carrefour-reunion.com"
base_url = "https://www.carrefour-reunion.com/page/magasins"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .find("script", type="text/json")
            .string
        )
        for x, _ in locations.items():
            yield SgRecord(
                page_url=base_url,
                store_number=x,
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                zip_postal=_["postcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="La Reunion",
                phone=_["main_phone"],
                location_type=_["brand"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(
                    bs(_["main_schedules"], "lxml").stripped_strings
                ),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
