from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kfc.by"
base_url = "https://www.kfc.by/restaurants/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var restaurants = restaurants(")[1]
            .split(");")[0]
        )
        for _ in locations:
            hours = f"{_['start_time']} - {_['finish_time']}"
            page_url = f"https://www.kfc.by/restaurants/{_['id']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"].replace("&quot;", '"'),
                city=_["city_name"],
                latitude=_["lat"],
                longitude=_["lon"],
                country_code="Belarus",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=_["value"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
