# -*- coding: utf-8 -*-
import time
from typing import Iterable, Tuple, Callable
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager


website = "pizzahut.cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://pizzahut.cl/pizzerias",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


class _SearchIteration(SearchIteration):
    """
    Here, you define what happens with each iteration of the search.
    The `do(...)` method is what you'd do inside of the `for location in search:` loop
    It provides you with all the data you could get from the search instance, as well as
    a method to register found locations.
    """

    def __init__(self, http: SgChrome):
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
        log.info(f"pulling data for coordinates: {lat},{lng}")

        rand_time = str(round(time.time() * 1000))
        api_url = "https://pizzahut.cl/localizador/getgeolocalizacionshops?latitude={}&longitude={}&_={}"

        self.__http.get(api_url.format(lat, lng, rand_time))

        try:
            json_res = json.loads(self.__http.find_element_by_tag_name("body").text)

            store_list = json_res["pos"]["markers"]

            for store in store_list:

                page_url = "https://pizzahut.cl/pizzerias" + store["url"]
                locator_domain = website

                raw_address = "<MISSING>"

                street_address = store["address"]
                city = "<MISSING>"
                state = store["lo_nombrprov"]
                zip = "<MISSING>"

                country_code = "CL"

                location_name = store["name"].strip()
                log.info(location_name)
                phone = store["phone"]
                store_number = store["id"]

                location_type = "<MISSING>"

                hours_of_operation = "<MISSING>"

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
                    raw_address=raw_address,
                )
        except:
            pass


def scrape():
    log.info("Started")
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
    )

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgChrome(
            executable_path=ChromeDriverManager().install(), is_headless=True
        ) as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=["CL"],
                max_threads=8,
            )

            for rec in par_search.run():
                writer.write_row(rec)


if __name__ == "__main__":
    scrape()
