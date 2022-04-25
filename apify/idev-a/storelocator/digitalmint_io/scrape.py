from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.digitalmint.io"
base_url = "https://storage.googleapis.com/marketing-json/map_data.json"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["features"]
        for _ in locations:
            addr = _["properties"]
            hours = []
            for hh in _["hours"]:
                hours.append(f"{hh['day']}: {hh['time']}")
            page_url = locator_domain + addr["url"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["machineDetails"]["operator"],
                street_address=addr["address"],
                city=addr["city"],
                state=addr["state"],
                zip_postal=addr["zipCode"],
                latitude=_["geometry"]["coordinates"][1],
                longitude=_["geometry"]["coordinates"][0],
                country_code=addr["country"],
                location_type=addr["locationType"],
                locator_domain=locator_domain,
                phone=addr["phone"],
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
