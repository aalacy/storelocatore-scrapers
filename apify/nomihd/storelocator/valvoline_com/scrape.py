# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import json

website = "valvoline.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "maps.locations.valvoline.com.prod.rioseo.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "*/*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://locations.valvoline.com.prod.rioseo.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://locations.valvoline.com.prod.rioseo.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


class _SearchIteration(SearchIteration):
    """
    Here, you define what happens with each iteration of the search.
    The `do(...)` method is what you'd do inside of the `for location in search:` loop
    It provides you with all the data you could get from the search instance, as well as
    a method to register found locations.
    """

    def __init__(self, http: SgRequests):
        self.__http = http
        self.__state = CrawlStateSingleton.get_instance()

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        log.info(f"fetching data for zipcode:{zipcode}")
        params = (
            ("template", "service"),
            ("level", "search"),
            ("search", zipcode),
        )

        api_url = (
            "https://maps.locations.valvoline.com.prod.rioseo.com/api/getAsyncLocations"
        )

        api_res = self.__http.get(api_url, headers=headers, params=params)
        if json.loads(api_res.text)["markers"]:
            maplist = json.loads(api_res.text)["maplist"]
            maplist = (
                "["
                + maplist.split('">')[1]
                .strip()
                .split(",</div>")[0]
                .strip()
                .replace('\\"', '"')
                .replace('"hours_sets": "', '"hours_sets": ')
                .replace('"specialties": "', '"specialties": ')
                .replace('"}"', '"}')
                .replace('"dst":null}"', '"dst":null}')
                .replace(']}"', "]}")
                + "]"
            )
            stores = json.loads(maplist, strict=False)

            for store in stores:
                location_name = store["location_name"]
                locator_domain = website
                store_number = store["lid"]

                page_url = store["website"]
                if not page_url:
                    page_url = "https://www.valvoline.com/en/locations/"
                location_type = "<MISSING>"

                phone = store["local_phone"]

                street_address = store.get("address_1", "<MISSING>")
                if store["address_2"] and len(store["address_2"]) > 0:
                    street_address = street_address + ", " + store["address_2"]

                city = store.get("city", "<MISSING>")

                state = store.get("region", "<MISSING>")
                zip = store.get("post_code", "<MISSING>")

                country_code = store.get("country_name", "<MISSING>")

                hours_list = []
                try:
                    hours = store["hours_sets"]["days"]
                    for day in hours.keys():
                        if isinstance(hours[day][0], dict):
                            time = (
                                hours[day][0]["open"] + " - " + hours[day][0]["close"]
                            )
                        elif isinstance(hours[day][0], str):
                            time = hours[day]

                        hours_list.append(day + ":" + time)
                except:
                    pass

                hours_of_operation = "; ".join(hours_list).strip()
                latitude, longitude = (
                    store["lat"],
                    store["lng"],
                )
                found_location_at(latitude, longitude)
                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    search_maker = DynamicSearchMaker(
        search_type="DynamicZipSearch",
        expected_search_radius_miles=20,
        max_search_results=25,
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404])) as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=[SearchableCountries.USA],
            )

            for rec in par_search.run():
                writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
