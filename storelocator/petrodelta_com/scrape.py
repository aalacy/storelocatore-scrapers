from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://petrodelta.com/"
urls = [
    "https://www.petrodelta.com/pa/wp-admin/admin-ajax.php?action=store_search&lat=8.53798&lng=-80.78213&max_results=100&search_radius=5000&autoload=1",
    "https://www.petrodelta.com/cr/wp-admin/admin-ajax.php?action=store_search&lat=8.53798&lng=-80.78213&max_results=100&search_radius=5000&autoload=1",
]


def fetch_data():
    with SgRequests() as session:
        for base_url in urls:
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                hours = []
                if _["hours"]:
                    for hh in bs(_["hours"], "lxml").select("table tr"):
                        hours.append(": ".join(hh.stripped_strings))
                yield SgRecord(
                    store_number=_["id"],
                    location_name=_["store"],
                    street_address=_["address"],
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
