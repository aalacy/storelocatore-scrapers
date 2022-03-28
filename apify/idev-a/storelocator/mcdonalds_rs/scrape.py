from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mcdonalds.rs"
base_url = "https://www.mcdonalds.rs/restorani/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var restaurantMarkers =")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )
        for _ in locations:
            hours_of_operation = "; ".join(
                bs(_["restaurant_worktime"], "lxml").stripped_strings
            )
            if "USKORO" in hours_of_operation:
                continue
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Serbia",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
