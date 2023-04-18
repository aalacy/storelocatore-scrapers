from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.nsbonline.com/"
    base_url = "https://www.nsbonline.com/search-locations"
    branch_url = "https://www.nsbonline.com/_/api/branches/41.4141911/-73.2995705/500"
    atm_url = "https://www.nsbonline.com/_/api/atms/41.4141911/-73.2995705/500"
    with SgRequests() as session:
        locations = session.get(atm_url, headers=_headers).json()
        for _ in locations["atms"]:
            yield SgRecord(
                page_url=base_url,
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["long"],
                country_code="US",
                location_type="ATM",
                locator_domain=locator_domain,
            )

        locations = session.get(branch_url, headers=_headers).json()
        for _ in locations["branches"]:
            if "No Branch, No ATM" in _["name"]:
                continue
            hours = []
            if _["description"]:
                hours = [
                    " ".join(hh.stripped_strings)
                    for hh in bs(_["description"], "lxml").select("ul")[0].select("li")
                ]
            yield SgRecord(
                page_url=base_url,
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["long"],
                country_code="US",
                location_type="Branch",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
