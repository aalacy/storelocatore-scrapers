from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import Grain_1_KM
from sglogging import SgLogSetup
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from typing import Iterable, Tuple, Callable

logger = SgLogSetup().get_logger("ditchwitch")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "http://ditchwitch.com/"
base_url = "https://www.ditchwitch.com/find-a-dealer"
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class ExampleSearchIteration(SearchIteration):
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:
        total = 0
        lat = coord[0]
        lng = coord[1]
        with SgRequests(verify_ssl=False, proxy_country="us") as http:
            current_country = current_country.upper()
            logger.info(f"[{current_country}] {lat, lng}")
            if current_country == "US":
                url = f"https://www.ditchwitch.com/wtgi.php?ajaxPage&ajaxAddress={zipcode}&lat={lat}&lng={lng}"
            else:
                url = f"https://www.ditchwitch.com/wtgi.php?ajaxPage&ajaxCountryCode={current_country}&ajaxCountryQuery={zipcode}&ajaxCountryLocal=false&lat={lat}&lng={lng}"
            res = http.get(url, headers=headers)
            if res.status_code != 200:
                return
            try:
                locations = res.json()
            except:
                return
            if "dealers" in locations:
                total += len(locations["dealers"])
                for loc in locations["dealers"]:
                    hours = []
                    for day in days:
                        day = day.lower()
                        if loc.get(f"{day}_open"):
                            open = loc[f"{day}_open"]
                            close = loc[f"{day}_open"]
                            if open:
                                times = f"{open} - {close}"
                            else:
                                times = "Not Listed"
                            hours.append(f"{day}: {times}")

                    street_address = loc["address1"]
                    if loc["address2"]:
                        street_address += " " + loc["address2"]
                    city = loc["city"]
                    if "Las Pinas City" in city:
                        city = "Las Pinas City"
                    if "MUNRO" in city:
                        city = "MUNRO"
                    if "ANDERBOLT" in city:
                        city = "ANDERBOLT"
                    yield SgRecord(
                        page_url=base_url,
                        store_number=loc["clientkey"],
                        location_name=loc["name"],
                        locator_domain=locator_domain,
                        street_address=street_address,
                        city=city,
                        state=loc["state"],
                        zip_postal=loc["postalcode"],
                        country_code=loc["country"],
                        phone=loc["phone"],
                        hours_of_operation="; ".join(hours),
                    )

                logger.info(
                    f"found: [{current_country}] {len(locations['dealers'])} | total: {total}"
                )


if __name__ == "__main__":
    countries = [
        "co",
        "cz",
        "ar",
        "au",
        "at",
        "bg",
        "ca",
        "es",
        "lb",
        "lt",
        "mx",
        "my",
        "nl",
        "nz",
        "ph",
        "pl",
        "ru",
        "sa",
        "se",
        "sg",
        "th",
        "tr",
        "ua",
        "us",
        "za",
    ]
    search_maker = DynamicSearchMaker(
        search_type="DynamicZipAndGeoSearch", granularity=Grain_1_KM()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=countries,
        )

        for rec in par_search.run():
            writer.write_row(rec)
