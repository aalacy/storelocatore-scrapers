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
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgpostal import sgpostal as parser


website = "boschcarservice.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "dl-emea.dxtservice.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
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
        log.info(f"cood:{lat},{lng}")
        search_url = "https://dl-emea.dxtservice.com/dl/api/search?latitude={}&longitude={}&searchRadius=100&includeStores=COUNTRY&pageIndex={}&pageSize=100&minDealers=10&maxDealers=20&storeTags=[103]"
        page_no = 0
        while True:

            stores_req = self.__http.get(
                search_url.format(lat, lng, page_no), headers=headers
            )
            try:
                status = json.loads(stores_req.text)["httpStatus"]
                if "No Content" == status or "External API error" == status:
                    break
                for store in json.loads(stores_req.text)["data"]["items"]:
                    page_url = "<MISSING>"
                    locator_domain = website
                    location_name = store["displayName"]
                    street_address = store["address"]["addressLine1"]

                    if (
                        "addressLine2" in store["address"]
                        and store["address"]["addressLine2"] is not None
                        and len(store["address"]["addressLine2"]) > 0
                    ):
                        street_address = (
                            street_address + ", " + store["address"]["addressLine2"]
                        )

                    city = store["address"]["city"]
                    state = store["address"]["state"]
                    zip = store["address"]["zipcode"]
                    raw_address = ""
                    if street_address and len(street_address) > 0:
                        raw_address = street_address
                    if city and len(city) > 0:
                        raw_address = raw_address + ", " + city
                    if state and len(state) > 0:
                        raw_address = raw_address + ", " + state
                    if zip and len(zip) > 0:
                        raw_address = raw_address + ", " + zip

                    formatted_addr = parser.parse_address_intl(raw_address)

                    city = formatted_addr.city
                    country_code = store["address"]["country"]
                    store_number = store["storeId"]
                    phone = store["address"]["officePhoneNumber"]
                    if not phone:
                        phone = store["address"]["mobilePhoneNumber"]

                    location_type = store["storeType"]
                    hours_dict = store["openingHours"]
                    hours_list = []
                    if hours_dict:
                        for key in hours_dict.keys():
                            day = key
                            time = ", ".join(hours_dict[day])
                            hours_list.append(day + ": " + time)

                    hours_of_operation = "; ".join(hours_list).strip()
                    latitude = store["geoCoordinates"]["latitude"]
                    longitude = store["geoCoordinates"]["longitude"]

                    found_location_at(lat, lng)
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
                log.error(stores_req.text)
                pass

            page_no = page_no + 1


def scrape():
    log.info("Started")
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=100,
        max_search_results=100,
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        countries = SearchableCountries.ALL
        for country in countries:
            with SgRequests(dont_retry_status_codes=([404])) as http:
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
