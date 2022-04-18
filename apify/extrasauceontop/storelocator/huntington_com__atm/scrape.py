from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_1_KM
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration


class ExampleSearchIteration(SearchIteration):
    def __init__(self, http: SgRequests):
        self.__http = http  # noqa
        self.__state = CrawlStateSingleton.get_instance()  # noqa

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,  # noqa
        current_country: str,  # noqa
        items_remaining: int,  # noqa
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:  # noqa
        lat = coord[0]
        long = coord[1]

        locator_domain = "https://www.huntington.com/"

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        }

        data = {
            "longitude": f"{str(long)}",
            "latitude": f"{str(lat)}",
            "typeFilter": "1,2",
            "envelopeFreeDepositsFilter": "false",
            "timeZoneOffset": "-180",
            "scController": "GetLocations",
            "scAction": "GetLocationsList",
        }

        r = http.post(
            "https://www.huntington.com/post/GetLocations/GetLocationsList",
            headers=headers,
            data=data,
        )
        try:
            js = r.json()["features"]
        except:
            return

        for j in js:
            a = j.get("properties")
            page_url = "https://www.huntington.com/branchlocator"
            location_name = a.get("LocName") or "<MISSING>"
            street_address = a.get("LocStreet") or "<MISSING>"
            city = a.get("LocCity") or "<MISSING>"
            state = a.get("LocState") or "<MISSING>"
            postal = a.get("LocZip") or "<MISSING>"
            country_code = "US"
            phone = a.get("LocPhone") or "<MISSING>"
            latitude = j.get("geometry").get("coordinates")[1]
            longitude = j.get("geometry").get("coordinates")[0]
            found_location_at(latitude, longitude)
            hours_of_operation = "<MISSING>"
            location_type = a.get("LocType") or "<MISSING>"
            if location_type == "1":
                location_type = "Branch"
            if location_type == "2":
                location_type = "ATM"
            store_number = a.get("LocID") or "<MISSING>"
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            tmp = []
            if a.get("SundayLobbyHours"):
                for d in days:
                    day = d
                    times = a.get(f"{d}LobbyHours")
                    line = f"{day} {times}"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)
            if hours_of_operation.count("24 Hours") == 7:
                hours_of_operation = "24 Hours"

            yield SgRecord(
                raw={
                    "locator_domain": locator_domain,
                    "page_url": page_url,
                    "location_name": location_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "city": city,
                    "store_number": store_number,
                    "street_address": street_address,
                    "state": state,
                    "zip": postal,
                    "phone": phone,
                    "location_type": location_type,
                    "hours": hours_of_operation,
                    "country_code": country_code,
                }
            )


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
                ],
            )
            #    max_threads=8)

            for rec in par_search.run():
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
