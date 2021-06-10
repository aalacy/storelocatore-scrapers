from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.townebank.com"


def _d(_, location_type="branch"):
    hours = []
    if _["LobbyHours"]:
        temp = [hh.strip() for hh in _["LobbyHours"].strip().split("\n") if hh.strip()]
        for x in range(0, len(temp), 2):
            hours.append(f"{temp[x]}: {temp[x+1]}")
    page_url = locator_domain + _["Url"]
    return SgRecord(
        page_url=page_url,
        location_name=_["LocationTitle"],
        street_address=_["Address"],
        city=_["City"],
        state=_["StateCode"],
        zip_postal=_["Zip"],
        latitude=_["Latitude"],
        longitude=_["Longitude"],
        country_code="US",
        location_type=location_type,
        phone=_.get("Telephone"),
        locator_domain=locator_domain,
        hours_of_operation="; ".join(hours),
    )


def fetch_data():
    atm_url = "https://www.townebank.com/api/search/searchlocations?latitude=0&longitude=0&locationType=ATMs"
    base_url = "https://www.townebank.com/api/search/searchlocations?latitude=0&longitude=0&locationType=Office+Locations"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["Locations"]:
            yield _d(_)

        session = SgRequests()
        locations = session.get(atm_url, headers=_headers).json()
        for _ in locations["Locations"]:
            yield _d(_, "atm")


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
