from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.altamed.org/"
base_url = "https://www.altamed.org/find/resultsJson?type=clinic&affiliates=yes"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["items"]:
            addr = _["address"].split(",")
            yield SgRecord(
                page_url="https://www.altamed.org/find/results?type=clinic&keywords=85281&affiliates=yes",
                store_number=_["ProviderKey"],
                location_name=_["name"],
                street_address=" ".join(addr[:-3]),
                city=addr[-3],
                state=addr[-2],
                zip_postal=addr[-1],
                latitude=_["lat"],
                longitude=_["lon"],
                country_code="US",
                phone=_["phone"],
                location_type=_["location_type"],
                locator_domain=locator_domain,
                hours_of_operation=_["den_work_hour"].replace(",", ";"),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
