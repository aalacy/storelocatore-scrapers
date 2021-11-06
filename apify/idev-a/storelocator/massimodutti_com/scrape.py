from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_2
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import SgLogSetup
from typing import Iterable, Tuple, Callable

logger = SgLogSetup().get_logger("massimodutti")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.massimodutti.com/"
base_url = "https://www.massimodutti.com/itxrest/2/bam/store/34009456/physical-store?appId=1&languageId=-1&latitude={}&longitude={}&favouriteStores=false&lastStores=false&closerStores=true&min=10&radioMax=100&receiveEcommerce=false&showBlockedMaxPackage=false"

days = [
    "",
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]


class ExampleSearchIteration(SearchIteration):
    def __init__(self):
        pass

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        with SgRequests(proxy_country="us") as http:
            lat = coord[0]
            lng = coord[1]
            res = http.get(base_url.format(lat, lng), headers=_headers)
            if res.status_code == 200:
                locations = res.json()["closerStores"]
                logger.info(f"{current_country, len(locations)}")
                if len(locations):
                    found_location_at(lat, lng)
                for store in locations:
                    hours = []
                    for hr in store.get("openingHours", {}).get("schedule", []):
                        times = f"{hr['timeStripList'][0]['initHour']} - {hr['timeStripList'][0]['endHour']}"
                        if len(hr["weekdays"]) == 1:
                            hh = hr["weekdays"][0]
                            hours.append(f"{days[hh]}: {times}")
                        else:
                            day = f'{days[hr["weekdays"][0]]} to {days[hr["weekdays"][-1]]}'
                            hours.append(f"{day}: {times}")
                    phone = ""
                    if store.get("phones"):
                        phone = store["phones"][0]

                    _streat = (
                        "-".join(store["name"].split())
                        .lower()
                        .replace(".", "")
                        .replace(",", "")
                    )
                    if store["state"]:
                        _state = "-".join(store["state"].split()).lower()
                    else:
                        _state = "-".join(store["city"].split()).lower()

                    page_url = f'https://www.massimodutti.com/us/store-locator/{_state}/{_streat}/{store["latitude"]},{store["longitude"]}/{store["id"]}'
                    yield SgRecord(
                        page_url=page_url,
                        store_number=store["id"],
                        location_name=store["name"],
                        street_address=" ".join(store["addressLines"]),
                        city=store["city"],
                        state=store["state"],
                        zip_postal=store["zipCode"],
                        latitude=store["latitude"],
                        longitude=store["longitude"],
                        phone=phone,
                        country_code=store["countryCode"],
                        hours_of_operation="; ".join(hours),
                        locator_domain=locator_domain,
                    )


if __name__ == "__main__":
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_2()
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=1000
        )
    ) as writer:
        search_iter = ExampleSearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=SearchableCountries.ALL,
        )

        for rec in par_search.run():
            writer.write_row(rec)
