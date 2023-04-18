from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.brownjugalaska.com/"
base_url = "https://www.brownjugalaska.net/wp-admin/admin-ajax.php?action=store_search&lat=61.2180556&lng=-149.9002778&max_results=250&search_radius=500&autoload=1"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers()).json()
        for _ in locations:
            hours = []
            for hour in bs(_["hours"], "lxml").select("tr"):
                hours.append(
                    f"{hour.select_one('td').text}: {hour.select('td')[1].text}"
                )
            hours_of_operation = "; ".join(hours)
            yield SgRecord(
                page_url=_.get("url", "<MISSING>"),
                store_number=_["id"],
                location_name=_["store"].replace("&#038;", ""),
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["zip"],
                country_code=_["country"],
                phone=_["phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
