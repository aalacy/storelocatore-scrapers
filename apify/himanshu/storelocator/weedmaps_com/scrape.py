# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration

website = "weedmaps.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
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

        lat = coord[0]
        lng = coord[1]
        log.info(f"coord:{lat},{lng}")
        search_url = "https://api-g.weedmaps.com/discovery/v2/listings?&filter%5Bbounding_radius%5D=75mi&filter%5Bbounding_latlng%5D={},{}&latlng={},{}&page_size=150&page={}"
        page_no = 1
        while True:

            try:
                jd = self.__http.get(
                    search_url.format(lat, lng, lat, lng, page_no), headers=headers
                )
                if isinstance(jd, SgRequestError):
                    break

                jd = jd.json()
                page_no += 1
                for loc in jd["data"]["listings"]:
                    locator_domain = website
                    location_name = loc["name"] if loc["name"] else "<MISSING>"
                    street_address = loc["address"] if loc["address"] else "<MISSING>"
                    city = loc["city"] if loc["city"] else "<MISSING>"
                    state = loc["state"] if loc["state"] else "<MISSING>"
                    zip = loc["zip_code"] if loc["zip_code"] else "<MISSING>"
                    country_code = loc.get("country", "<MISSING>")
                    store_number = loc["id"]
                    phone = loc["phone_number"] if loc["phone_number"] else "<MISSING>"
                    location_type = loc["type"] if loc["type"] else "<MISSING>"
                    latitude = loc["latitude"] if loc["latitude"] else "<MISSING>"
                    longitude = loc["longitude"] if loc["longitude"] else "<MISSING>"
                    hours_list = []

                    try:
                        days = loc["business_hours"].keys()
                        for day in days:
                            time = (
                                loc["business_hours"][day]["open"]
                                + "-"
                                + loc["business_hours"][day]["close"]
                            )
                            hours_list.append(day + ": " + time)

                    except:
                        pass
                    hours_of_operation = "; ".join(hours_list).strip()
                    page_url = loc["web_url"] if loc["web_url"] else "<MISSING>"

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

            except:
                raise


def scrape():
    log.info("Started")
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=100,
        max_search_results=150,
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        countries = SearchableCountries.ALL
        for country in countries:
            with SgRequests(dont_retry_status_codes=([404, 422])) as http:
                search_iter = _SearchIteration(http=http)
                par_search = ParallelDynamicSearch(
                    search_maker=search_maker,
                    search_iteration=search_iter,
                    country_codes=[country],
                )

                for rec in par_search.run():
                    writer.write_row(rec)


if __name__ == "__main__":
    scrape()
