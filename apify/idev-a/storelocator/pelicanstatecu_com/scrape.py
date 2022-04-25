from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pelicanstatecu.com"
atm_url = "https://www.pelicanstatecu.com/_/api/atms/37.0891751/-95.71327219999999/5000"
branch_url = (
    "https://www.pelicanstatecu.com/_/api/branches/37.0891751/-95.71327219999999/5000"
)


def fetch_data():
    with SgRequests() as session:
        locations = session.get(atm_url, headers=_headers).json()["atms"]
        for _ in locations:
            yield SgRecord(
                page_url="https://www.pelicanstatecu.com/locations",
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                location_type="atm",
                latitude=_["lat"],
                longitude=_["long"],
                country_code="US",
                locator_domain=locator_domain,
            )

        locations = session.get(branch_url, headers=_headers).json()["branches"]
        for _ in locations:
            page_url = "https://www.pelicanstatecu.com/locations"
            hours = ""
            if "temporarily closed" in _["description"]:
                hours = "temporarily closed"
            elif _["description"]:
                info = bs(_["description"], "lxml")
                _hr = info.find("b", string=re.compile(r"^Lobby Hours:"))
                if _hr:
                    hours = " ".join(
                        _hr.find_parent("div").find_next_sibling().stripped_strings
                    )
                page_url = info.a["href"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                location_type="branch",
                latitude=_["lat"],
                phone=_["phone"],
                longitude=_["long"],
                country_code="US",
                hours_of_operation=hours,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
