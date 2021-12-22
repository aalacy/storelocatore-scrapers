from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.t-systems.com"
base_url = "https://www.t-systems.com/service/search/ts-gb-en/111596?ajax=true"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["results"]
        for _ in locations:
            yield SgRecord(
                page_url=_.get("url"),
                location_name=_["title"],
                street_address=(_["houseNr"] + " " + _["street"]).strip(),
                city=_["city"],
                state=_.get("state"),
                zip_postal=_.get("zipCode"),
                latitude=_["latLong"].split(",")[0].strip(),
                longitude=_["latLong"].split(",")[1].strip(),
                country_code=_["countryCode"],
                phone=_.get("telephone"),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
