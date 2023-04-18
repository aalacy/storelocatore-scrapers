from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _s(val):
    return (
        val.split("(")[0]
        .replace("Crest Industries", "")
        .replace("Cabrini Hospital", "")
        .replace("Rapides Parish Courthouse, 3rd floor", "")
        .replace("England Airpark", "")
        .replace("Scott's Ace Hardware", "")
        .strip()
    )


def fetch_data():
    locator_domain = "https://www.redriverbank.net/"
    page_url = "https://www.redriverbank.net/locations/#bh-sl-loc-list"
    base_url = "https://www.redriverbank.net/dist/data/locations.json?formattedAddress=&boundsNorthEast=&boundsSouthWest="
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"] and _["address2"] not in street_address:
                street_address += " " + _["address2"]
            location_type = ["branch"]
            if _["atm"]:
                location_type.append(_["atm"])
            if "ATM" in _["name"]:
                location_type = ["atm"]
            hours = []
            if _["hours1"]:
                hours += list(bs(_["hours1"], "lxml").stripped_strings)
            elif _["hours2"]:
                hours += list(bs(_["hours2"], "lxml").stripped_strings)
            elif _["hours3"]:
                hours += list(bs(_["hours3"], "lxml").stripped_strings)
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["id"],
                street_address=_s(street_address),
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                location_type=", ".join(location_type),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
