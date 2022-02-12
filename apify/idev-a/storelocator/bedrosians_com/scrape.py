from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.bedrosians.com"
base_url = "https://www.bedrosians.com/en/our-locations/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split('value("locations",')[1]
            .split(");")[0]
            .strip()
        )
        for _ in locations:
            hours = ""
            if _["operations"]:
                hours = _["operations"][0]["timeofoperation"]
            yield SgRecord(
                page_url=_["branchaddressurl"],
                store_number=_["locationcode"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation=hours.replace("\n", "; ").replace("\r", ""),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
