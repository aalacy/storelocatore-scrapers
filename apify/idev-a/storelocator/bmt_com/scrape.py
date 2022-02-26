from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.bmt.com/"
    base_url = "https://www.bmt.com/wp-admin/admin-ajax.php?action=store_search&lat=40.023024&lng=-75.315177&max_results=100&search_radius=50&autoload=1"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            for hh in bs(_["custom_hours"], "lxml").select("ul")[0].select("li"):
                hours.append(
                    f"{hh.select_one('.day').text.strip()} {hh.select_one('.hours').text.strip()}"
                )
            yield SgRecord(
                page_url=_["permalink"],
                location_name=_["store"],
                store_number=_["id"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=bs(_["category"], "lxml").text,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
