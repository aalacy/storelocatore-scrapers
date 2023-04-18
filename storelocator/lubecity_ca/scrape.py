from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.lubecity.ca"
base_url = "https://www.lubecity.ca/wp-admin/admin-ajax.php?action=store_search&lat=52.26897&lng=-113.81156&max_results=50&search_radius=50&autoload=1"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            if _["hours"]:
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in bs(_["hours"], "lxml").select("table tr")
                ]
            location_name = _["store"].replace("&#8211;", "-")
            location_type = ""
            if "CLOSED" in location_name:
                location_type = "CLOSED"
            yield SgRecord(
                page_url=_["permalink"],
                store_number=_["id"],
                location_name=location_name,
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
