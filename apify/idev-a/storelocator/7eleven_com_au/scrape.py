from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.7eleven.com.au"
base_url = "https://www.7eleven.com.au/storelocator-retail/mulesoft/stores?lat=-33.8688197&long=151.2092955&dist=10000"
days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["stores"]
        for _ in locations:
            street_address = _["address"]["address1"]
            if _["address"]["address2"]:
                street_address += " " + _["address"]["address2"]
            hours = []
            if _["allHours"]:
                hours = ["24 hours"]
            else:
                for hh in _["openingHours"]:
                    hours.append(
                        f"{days[hh['day_of_week']]}: {hh['start_time']} - {hh['end_time']}"
                    )
            yield SgRecord(
                page_url="https://www.7eleven.com.au/store-locator.html",
                store_number=_["storeId"],
                location_name=_["name"],
                street_address=street_address,
                city=_["address"]["suburb"],
                state=_["address"]["state"],
                zip_postal=_["address"]["postcode"],
                latitude=_["location"][0],
                longitude=_["location"][1],
                country_code="Australia",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
