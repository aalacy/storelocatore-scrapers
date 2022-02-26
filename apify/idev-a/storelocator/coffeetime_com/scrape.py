from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("coffeetime")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.coffeetime.com"
base_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=YDGUJSNDOUAFKPRL&center={},{}&coordinates={},{},{},{}&multi_account=false&page=1&pageSize=300"
days = ["", "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


def fetch_data(search):
    for lat, lng in search:
        x1 = lat - 0.62878579728
        x2 = lng + 0.62226070663
        y1 = lat + 1.10275268555
        y2 = lng - 1.10275268555
        with SgRequests() as session:
            links = session.get(
                base_url.format(lat, lng, x1, y1, x2, y2), headers=_headers
            ).json()
            logger.info(f"{len(links)} found")

            logger.info(f"[{lat, lng}] {len(links)}")
            for _ in links:
                page_url = "https://locations.coffeetime.com" + _["llp_url"]
                if _["open_or_closed"] == "coming soon":
                    continue
                temp = {}
                hours = []
                for hh in _["store_info"]["hours"].split(";"):
                    if not hh:
                        continue
                    time1 = hh.split(",")[1][:2] + ":" + hh.split(",")[1][2:]
                    time2 = hh.split(",")[2][:2] + ":" + hh.split(",")[2][2:]
                    temp[days[int(hh.split(",")[0])]] = f"{time1}-{time2}"
                for day in days:
                    if not day:
                        continue
                    if temp.get(day):
                        hours.append(f"{day}: {temp[day]}")
                    else:
                        hours.append(f"{day}: closed")

                if not hours:
                    hours = ["Mon-Sun: Closed"]

                info = _["store_info"]
                location_name = ""
                for nn in _["custom_fields"]:
                    if nn["name"] == "StoreName":
                        location_name = nn["data"]
                        break

                search.found_location_at(info["latitude"], info["longitude"])
                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=f"{info['address']} {info.get('address_extended', '')} {info.get('address3', '')}".strip(),
                    city=info["locality"],
                    state=info["region"],
                    zip_postal=info["postcode"],
                    country_code=info["country"],
                    phone=info["phone"],
                    latitude=info["latitude"],
                    longitude=info["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=10
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=500
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
