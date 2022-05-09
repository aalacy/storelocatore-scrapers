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

locator_domain = "https://tommys-express.com"
base_url = "https://tommys-express.com/assets/php/locations.php"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("script#location-json")
            .string
        )
        for key, loc in locations.items():
            for _ in loc[1]:
                if not _["open"]:
                    continue
                hours = []
                for hh in _["hours"]:
                    hours.append(f"{hh['day']}: {hh['open']}-{hh['close']}")
                yield SgRecord(
                    page_url=f"https://tommys-express.com/locations/{_['id'].lower()}",
                    store_number=_["id"],
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_["state"],
                    zip_postal=_["zip"],
                    latitude=_["lat"],
                    longitude=_["long"],
                    country_code=_["country"],
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
