# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration


website = "vpz.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "vpz-shopify.ayko.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "origin": "https://vpz.co.uk",
    "referer": "https://vpz.co.uk/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


class _SearchIteration(SearchIteration):
    """
    Here, you define what happens with each iteration of the search.
    The `do(...)` method is what you'd do inside of the `for location in search:` loop
    It provides you with all the data you could get from the search instance, as well as
    a method to register found locations.
    """

    def __init__(self):
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
        log.info(f"fetching data using coordinates:{lat},{lng}")
        params = {
            "latitude": lat,
            "longitude": lng,
        }
        search_url = "https://vpz-shopify.ayko.com/api/location/get"
        with SgRequests(dont_retry_status_codes=([404])) as session:
            stores_req = session.get(search_url, headers=headers, params=params)

            try:
                stores = json.loads(stores_req.text)
                for key in stores.keys():
                    store_info = stores[key]
                    page_url = "<MISSING>"
                    locator_domain = website
                    location_name = store_info["name"]
                    street_address = store_info["address_1"]
                    if (
                        "address_2" in store_info
                        and store_info["address_2"]
                        and len(store_info["address_2"]) > 0
                    ):
                        street_address = street_address + ", " + store_info["address_2"]

                    city = store_info["town"]
                    state = store_info["county"]
                    zip = store_info["postcode"]
                    country_code = "GB"
                    store_number = store_info["location_id"]
                    phone = store_info["phone_number"]
                    location_type = "<MISSING>"
                    if store_info["is_active"] != "1":
                        location_type = "not active"

                    hours_of_operation = "<MISSING>"

                    latitude = store_info["latitude"]
                    longitude = store_info["longitude"]

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
                pass


def scrape():
    log.info("Started")
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=50,
    )

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        search_iter = _SearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=["GB"],
        )

        for rec in par_search.run():
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
