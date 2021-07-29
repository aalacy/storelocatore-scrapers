from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.phoenix.edu"
base_url = "https://www.phoenix.edu/api/plct/3/uopx/locations?type=site&page.size=100"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["results"]
        for loc in locations:
            _ = loc["attributes"]
            street_address = _["addressLine2"]
            if _.get("addressLine3"):
                street_address += " " + _["addressLine3"]
            yield SgRecord(
                page_url=_["ref"],
                location_name=_["altName"],
                street_address=street_address,
                city=_["city"],
                state=_["stateProvince"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=loc["countryCode"],
                phone=_.get("phoneLocal"),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
