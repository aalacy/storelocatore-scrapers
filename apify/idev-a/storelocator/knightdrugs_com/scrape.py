from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "http://www.knightdrugs.com/"
    base_url = "http://www.knightdrugs.com/wp-admin/admin-ajax.php?action=store_search&lat=42.33143&lng=-83.04575&max_results=25&search_radius=50&autoload=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in bs(_["hours"], "lxml").select("tr")
            ]
            yield SgRecord(
                page_url="https://www.altamed.org/find/results?type=clinic&keywords=85281&affiliates=yes",
                location_name=_["store"],
                store_number=_["id"],
                street_address=street_address.replace(",", ""),
                city=_["city"].replace(",", ""),
                state=_["state"].replace(",", ""),
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
