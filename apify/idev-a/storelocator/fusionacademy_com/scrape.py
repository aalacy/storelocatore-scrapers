from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.fusionacademy.com/campuses/"
base_url = "https://www.fusionacademy.com/wp-admin/admin-ajax.php?lang=global&action=store_search&lat=42.96479&lng=-85.66924&max_results=100000&search_radius=30&autoload=1"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += _["address2"]
            if street_address.strip().endswith(","):
                street_address = street_address[:-1]
            hours = []
            if _["hours"]:
                for hh in bs(_["hours"], "lxml").select("tr"):
                    hours.append(": ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=_["url"],
                store_number=_["id"],
                location_name=_["store"].replace("&#8211;", "-"),
                street_address=street_address.replace("&#8211;", "-"),
                city=_["city"].replace(",", "").replace("&#8211;", "-"),
                state=_["state"],
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_.get("phone"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
