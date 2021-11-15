from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://dunkin.ae/find-us/"
base_url = "https://dunkin.ae/wp-admin/admin-ajax.php?action=store_search&lat=25.20485&lng=55.27078&max_results=100&search_radius=500&autoload=1"

cities = [
    "Dubai",
    "SHJ",
    "Sharjah",
    "UAQ",
    "Umm Al Quwain",
    "AUH",
    "Abu Dhabi",
    "RAK",
    "Ras Al Khaimah",
    "Al Ain",
    "AAN",
]


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = [
                aa.strip()
                for aa in _["address"].replace("-", ",").split(",")
                if aa.strip()
            ]
            if addr[-1] in cities:
                del addr[-1]
            addr = [aa.strip() for aa in ", ".join(addr).split(" ") if aa.strip()]
            if addr[-1] in cities:
                del addr[-1]

            hours = []
            if _["hours"]:
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in bs(_["hours"], "lxml").select("table tr")
                ]
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["store"].replace("&#8211;", "-"),
                street_address=" ".join(addr),
                city=_["city"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="UAE",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
