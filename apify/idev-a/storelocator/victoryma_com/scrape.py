from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.victoryma.com"
base_url = "https://www.victoryma.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=3000"

coords = [("39.47", "-0.36"), ("-33.62", "150.83"), ("28.43", "-81.26")]


def fetch_data():
    for lat, lng in coords:
        with SgRequests() as session:
            locations = session.get(base_url.format(lat, lng), headers=_headers).json()
            logger.info(f"[{lat, lng}] {len(locations)}")
            for _ in locations:
                street_address = _["address"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in bs(_["hours"], "lxml").select("table tr")
                ]
                yield SgRecord(
                    page_url=_["url"],
                    store_number=_["id"],
                    location_name=_["store"],
                    street_address=street_address,
                    city=_["city"].replace(",", ""),
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
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
