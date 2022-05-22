from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.co.nz"
base_url = "https://mcdonalds.co.nz/data/store"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            latlng = _["store_geocode"].split(",")
            hours = []
            if _["store_trading_hour"]:
                for hh in _["store_trading_hour"][1:]:
                    times = f"{hh[1]} - {hh[2]}"
                    if not hh[1]:
                        times = "closed"
                    hours.append(f"{hh[0]}: {times}")

            city = _["store_suburb"].replace('"', "").split(",")[0].strip()
            street_address = _["store_address"]
            if "COLOMBO" in city or "CENTRE" in city:
                street_address += " " + city
                city = ""
            if not city and _["store_state"] != "NEW ZEALAND":
                city = _["store_state"]
            yield SgRecord(
                page_url="https://mcdonalds.co.nz/find-us/restaurants",
                store_number=_["nid"],
                location_name=_["title"],
                street_address=street_address,
                city=city,
                latitude=latlng[0],
                longitude=latlng[1],
                country_code="NZ",
                phone=_["store_phone"].split("TAKE")[0],
                location_type=_["store_building_type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
