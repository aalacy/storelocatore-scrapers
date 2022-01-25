from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4

logger = SgLogSetup().get_logger("carrossier")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://carrossier-procolor.com/"
base_url = "https://www.procolor.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=50&search_radius=6000&filter={}&autoload=1"

country_map = {"us": "129", "ca": "128"}


def fetch_data(search):
    for lat, lng in search:
        with SgRequests(proxy_country="us") as session:
            _filter = country_map[search.current_country()]
            url = base_url.format(lat, lng, _filter)
            try:
                locations = session.get(url, headers=_headers).json()
            except:
                continue
            logger.info(f"[{search.current_country()}] {len(locations)} found")
            for _ in locations:
                search.found_location_at(_["lat"], _["lng"])
                hours = []
                if _["hours"]:
                    for hh in bs(_["hours"], "lxml").select("tr"):
                        hours.append(": ".join(hh.stripped_strings))
                street_address = _["address"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                location_name = _["store"].replace("&#8217;", "'")
                slug = (
                    location_name.replace("'", "")
                    .replace("é", "e")
                    .replace("ô", "o")
                    .replace("/", "")
                    .lower()
                )
                slug = "-".join([ss.strip() for ss in slug.split() if ss.strip()])
                page_url = f"https://www.procolor.com/en-ca/shop/{slug}/"
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=_["store"].replace("&#8217;", "'"),
                    street_address=street_address,
                    city=_["city"].strip(),
                    state=_["state"].strip(),
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
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
            granularity=Grain_4(),
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
