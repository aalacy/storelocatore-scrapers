from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.lakecitybank.com"
base_url = "https://locations.lakecitybank.com/"
json_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=1000&location={}&limit=50&api_key={}&v=20181201&resolvePlaceholders=true&savedFilterIds=28134189"


def fetch_data(search):
    for zipcode in search:
        with SgRequests() as session:
            api_key = (
                session.get(base_url, headers=_headers)
                .text.split("var liveAPIKey =")[1]
                .split(".trim(")[0]
                .strip()[1:-1]
            )
            locations = session.get(
                json_url.format(zipcode, api_key), headers=_headers
            ).json()["response"]["entities"]
            logger.info(f"[{zipcode}] {len(locations)}")
            for _ in locations:
                hours = []
                for day, times in _["hours"].items():
                    if day == "holidayHours":
                        break
                    if times.get("isClosed"):
                        hh = "closed"
                    else:
                        hh = f"{times['openIntervals'][0]['start']}-{times['openIntervals'][0]['end']}"
                    hours.append(f"{day}: {hh}")

                coord = {}
                if "geocodedCoordinate" in _:
                    coord = _["geocodedCoordinate"]
                elif "cityCoordinate" in _:
                    coord = _["cityCoordinate"]
                location_name = _["name"]
                if "CLOSED" in location_name:
                    hours = ["Closed"]

                search.found_location_at(coord["latitude"], coord["longitude"])
                yield SgRecord(
                    page_url=_["websiteUrl"]["url"],
                    location_name=location_name.replace("CLOSED", ""),
                    street_address=_["address"]["line1"],
                    city=_["address"]["city"],
                    state=_["address"]["region"],
                    zip_postal=_["address"]["postalCode"],
                    country_code=_["address"]["countryCode"],
                    latitude=coord["latitude"],
                    longitude=coord["longitude"],
                    phone=_["mainPhone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        search = DynamicZipSearch(
            country_codes=["us"], expected_search_radius_miles=500
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)
