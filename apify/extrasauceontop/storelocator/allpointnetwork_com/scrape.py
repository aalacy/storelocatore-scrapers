from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_1_KM
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import time


class ExampleSearchIteration(SearchIteration):
    def __init__(self, http: SgRequests):
        self.__http = http  # noqa
        self.__state = CrawlStateSingleton.get_instance()

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,  # noqa
        current_country: str,
        items_remaining: int,  # noqa
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:  # noqa

        url = "https://clsws.locatorsearch.net/Rest/LocatorSearchAPI.svc/GetLocations"

        x = 0
        search_lat = coord[0]
        search_lon = coord[1]
        while True:
            x = x + 1
            params = {
                "Latitude": str(search_lat),
                "Longitude": str(search_lon),
                "Miles": "100",
                "NetworkId": "10029",
                "PageIndex": str(x),
                "SearchByOptions": "",
            }

            y = 0
            while True:
                y = y + 1
                if y % 10 == 0:
                    time.sleep(1)

                if y == 50:
                    raise Exception
                response_obj = http.post(url, json=params)

                if response_obj.status_code != 200:
                    continue

                response = response_obj.json()
                break

            try:
                for location in response["data"]["ATMInfo"]:
                    locator_domain = "allpointnetwork.com"
                    page_url = "https://clsws.locatorsearch.net/Rest/LocatorSearchAPI.svc/GetLocations"
                    location_name = "Allpoint " + location["RetailOutlet"]
                    address = location["Street"]
                    city = location["City"]
                    state = location["State"]
                    zipp = location["ZipCode"]
                    country_code = location["Country"]
                    if country_code == "MX":
                        continue
                    store_number = location["LocationID"]
                    phone = "<MISSING>"
                    location_type = location["RetailOutlet"]
                    latitude = location["Latitude"]
                    longitude = location["Longitude"]
                    hours = "<MISSING>"
                    rec_count = self.__state.get_misc_value(
                        current_country, default_factory=lambda: 0
                    )
                    self.__state.set_misc_value(current_country, rec_count + 1)

                    yield SgRecord(
                        raw={
                            "locator_domain": locator_domain,
                            "page_url": page_url,
                            "location_name": location_name,
                            "latitude": latitude,
                            "longitude": longitude,
                            "city": city,
                            "store_number": store_number,
                            "street_address": address,
                            "state": state,
                            "zip": zipp,
                            "phone": phone,
                            "location_type": location_type,
                            "hours": hours,
                            "country_code": country_code,
                        }
                    )

                if len(response["data"]["ATMInfo"]) < 100:
                    break
            except Exception:
                break


if __name__ == "__main__":
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", granularity=Grain_1_KM()
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        with SgRequests() as http:
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=[
                    SearchableCountries.USA,
                    SearchableCountries.CANADA,
                    SearchableCountries.BRITAIN,
                ],
            )
            #    max_threads=8)

            for rec in par_search.run():
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
