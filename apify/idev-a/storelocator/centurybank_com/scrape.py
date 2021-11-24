from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.centurybank.com/"
    atm_url = "https://www.centurybank.com/_/api/atms/42.4021807/-71.0970849/50"
    branch_url = "https://www.centurybank.com/_/api/branches/42.4021807/-71.0970849/50"
    page_url = "https://www.centurybank.com/locator"
    with SgRequests() as session:
        locations = session.get(atm_url, headers=_headers).json()
        for _ in locations["atms"]:
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["long"],
                country_code="US",
                location_type="atm",
                locator_domain=locator_domain,
            )

        locations = session.get(branch_url, headers=_headers).json()
        for _ in locations["branches"]:
            temp = list(bs(_["description"], "lxml").stripped_strings)
            if temp and "Lobby" in temp[0]:
                del temp[0]
            hours = []
            for hh in temp:
                if "Drive" in hh:
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["long"],
                country_code="US",
                location_type="branch",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
