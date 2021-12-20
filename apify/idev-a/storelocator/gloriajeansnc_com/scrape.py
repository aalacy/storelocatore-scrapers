from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.gloriajeansnc.com"
base_url = "https://www.gloriajeansnc.com/wp-admin/admin-ajax.php?action=store_search&lat=35.18735&lng=33.35061&max_results=25&search_radius=10&autoload=1"


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
            yield SgRecord(
                page_url="https://www.gloriajeansnc.com/gjc-magazalarimiz/",
                store_number=_["id"],
                location_name=_["store"].replace("&#8217;", "'"),
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
