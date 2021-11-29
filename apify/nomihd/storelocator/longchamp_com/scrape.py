# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import SearchableCountries, Grain_1_KM
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "longchamp.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.longchamp.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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
        log.info(f"coord:{lat},{lng}")
        search_url = "https://www.longchamp.com/on/demandware.store/Sites-Longchamp-NA-Site/en_US/Stores-FindStores"
        params = (
            ("showMap", "true"),
            ("findInStore", "false"),
            ("productId", "false"),
            ("checkboxStore", "stock"),
            ("radius", "300"),
            ("lat", lat),
            ("lng", lng),
            ("entityType", "Place"),
            ("entitySubType", ""),
            ("countryRegion", ""),
            ("formattedSuggestion", ""),
        )
        try:
            with SgRequests(
                dont_retry_status_codes=([404]), proxy_country="us"
            ) as session:
                session.get(
                    "https://www.longchamp.com/us/en/stores?showMap=true",
                    headers=headers,
                )

                stores_req = SgRequests.raise_on_err(
                    session.get(search_url, params=params)
                )
                stores = json.loads(stores_req.text)["stores"]
                for store in stores:
                    if store["type"] != "BTQ":
                        continue
                    page_url = "<MISSING>"
                    locator_domain = website
                    location_name = store["name"]
                    street_address = store["address1"]
                    if store["address2"] is not None and len(store["address2"]) > 0:
                        if street_address:
                            street_address = street_address + ", " + store["address2"]
                        else:
                            street_address = store["address2"]

                    city = store.get("city", "<MISSING>")
                    state = store.get("stateCode", "<MISSING>")
                    zip = store.get("postalCode", "<MISSING>")
                    country_code = store["countryCode"]
                    if country_code == "" or country_code is None:
                        country_code = current_country

                    store_number = store["ID"]
                    phone = store.get("phone", "<MISSING>")

                    location_type = "<MISSING>"
                    hours_list = []
                    hours = store.get("storeHours", [])
                    days_dict = {
                        "1": "Sunday",
                        "2": "Monday",
                        "3": "Tuesday",
                        "4": "Wednesday",
                        "5": "Thursday",
                        "6": "Friday",
                        "7": "Saturday",
                    }
                    for hour in hours:
                        day = days_dict.get(hour["day"])
                        if (
                            len(hour["openingTime"].strip()) <= 0
                            and len(hour["closingtime"].strip()) <= 0
                        ):
                            time = "Closed"
                        else:
                            time = hour["openingTime"] + "-" + hour["closingtime"]

                        if day:
                            hours_list.append(day + ":" + time)

                    hours_of_operation = "; ".join(hours_list).strip()
                    latitude = store["latitude"]
                    longitude = store["longitude"]

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

        except SgRequestError:
            pass


def scrape():
    log.info("Started")
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=50,
        granularity=Grain_1_KM(),
    )

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:

        search_iter = _SearchIteration()
        par_search = ParallelDynamicSearch(
            search_maker=search_maker,
            search_iteration=search_iter,
            country_codes=SearchableCountries.ALL,
        )

        for rec in par_search.run():
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
