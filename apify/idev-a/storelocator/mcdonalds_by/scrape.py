from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.by"
base_url = "https://mcdonalds.by/en/restaurants.html"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var _mapMarkers =")[1]
            .split("||")[0]
            .strip()
        )
        for _ in locations:
            hours_of_operation = ""
            if _["time"]:
                hours_of_operation = (
                    _["time"]
                    .split("McDrive")[0]
                    .replace("Restaurant:", "")
                    .replace("—", "-")
                )
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="Belarus",
                phone=_["phones"][0].split(",")[0],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
