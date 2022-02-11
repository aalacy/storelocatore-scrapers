# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from datetime import datetime as dt
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import retry, stop_after_attempt

website = "raymourflanigan.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}


def retry_error_callback(retry_state):
    postal = retry_state.args[0]
    log.error(f"Failure to fetch locations for: {postal}")
    return []


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

    @retry(retry_error_callback=retry_error_callback, stop=stop_after_attempt(5))
    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:

        if len(zipcode) == 1:
            zipcode = "0000" + zipcode
        if len(zipcode) == 2:
            zipcode = "000" + zipcode
        if len(zipcode) == 3:
            zipcode = "00" + zipcode
        if len(zipcode) == 4:
            zipcode = "0" + zipcode

        log.info(f"pulling data for zipcode: {zipcode}")
        url = "https://www.raymourflanigan.com/api/custom/location-search"
        params = {
            "postalCode": zipcode,
            "distance": 100,
            "includeShowroomLocations": True,
            "includeOutletLocations": True,
            "includeClearanceLocations": True,
            "includeAppointments": True,
        }
        stores = self.__http.get(url, params=params, headers=headers).json()[
            "locations"
        ]

        for store in stores:
            page_url = "https://www.raymourflanigan.com" + store["url"]
            log.info(page_url)
            locator_domain = website
            location_name = store["displayName"]
            street_address = store["addressLine1"]
            if (
                "addressLine2" in store
                and store["addressLine2"] is not None
                and len(store["addressLine2"]) > 0
            ):
                street_address = street_address + ", " + store["addressLine2"]

            city = store["city"]
            state = store["stateProvince"]
            zip = store["postalCode"]
            country_code = "US"

            store_number = store["businessUnitCode"]
            phone = store["phoneNumber"]

            location_type = "Showroom"
            if store["clearanceCenter"] is True:
                location_type = "Clearance Center"
            if store["outlet"] is True:
                location_type = "Outlet"

            location_name = "Raymour & Flanigan " + location_type
            hours_of_operation = ""
            hours = store["hours"]
            hours_list = []
            for key, hour in hours.items():
                if isinstance(hours[key], dict):
                    if hours[key] and hours[key]["open"] and hours[key]["close"]:
                        day = key
                        if day != "today":
                            hours_list.append(
                                day
                                + ":"
                                + hours[key]["open"]
                                + "-"
                                + hours[key]["close"]
                            )
            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["latitude"]
            longitude = store["longitude"]
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
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(search_type="DynamicZipSearch")

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
    start = dt.now()
    scrape()
    log.info(f"duration: {dt.now() - start}")
