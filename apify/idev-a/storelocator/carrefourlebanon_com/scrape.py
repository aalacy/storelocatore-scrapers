from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.carrefourlebanon.com"
base_url = "https://www.carrefourlebanon.com/maflbn/en/store-finder?q=beirut&page=0&storeFormat="


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["data"]
        for _ in locations:
            street_address = _["line1"]
            if _["line2"]:
                street_address += " " + _["line2"]
            hours = []
            for day, hh in _["openings"].items():
                hours.append(f"{day}: {hh}")
            location_name = f"Carrefor {_['storeFormat']} {_['displayName']}"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                city=_["town"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Lebanon",
                phone=_["phone"],
                location_type=_["storeFormat"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
