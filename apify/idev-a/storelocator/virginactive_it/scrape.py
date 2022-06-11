from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.virginactive.it"
base_url = "https://www.virginactive.it/Virgin/Clubs/GetAllClubs"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["getAllClubsResult"][
            "obj"
        ]
        for _ in locations:
            addr = _["address"]
            location_type = ""
            if _["isTemporaryClosed"]:
                location_type = "Temporarily Closed"
            yield SgRecord(
                page_url=_["detailPageUrl"],
                store_number=_["id"],
                location_name=_["name"],
                street_address=addr["Street"],
                city=addr["City"],
                state=addr["StateCode"],
                zip_postal=addr["ZipCode"],
                latitude=addr["Latitude"],
                longitude=addr["Longitude"],
                country_code="IT",
                locator_domain=locator_domain,
                location_type=location_type,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
