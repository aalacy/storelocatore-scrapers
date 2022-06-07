from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://refuelyourday.com"
base_url = "https://refuelyourday.com/wp-admin/admin-ajax.php?action=store_search&lat=38.81505&lng=-90.955972&max_results=25&search_radius=50&autoload=1"


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            state = _["state"]
            if state == "&lt;P":
                state = ""
            yield SgRecord(
                page_url="https://refuelyourday.com/locations/",
                store_number=_["id"],
                location_name=_["store"].replace("&#8217;", "'").replace("&#038;", "&"),
                street_address=street_address,
                city=_["city"],
                state=state,
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"] or "USA",
                phone=_p(_["phone"]),
                locator_domain=locator_domain,
                hours_of_operation=_["hours"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
