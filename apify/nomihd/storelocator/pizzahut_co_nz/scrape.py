# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgpostal import sgpostal as parser

website = "pizzahut.co.nz"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "apiapse2.phdvasia.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/plain, */*",
    "lang": "en",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "client": "2f28344b-2d60-4754-8985-5c23864a3737",
    "origin": "https://pizzahut.co.nz",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://pizzahut.co.nz/",
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
        log.info(f"pulling data for coordinates: {lat},{lng}")
        search_url = "https://apiapse2.phdvasia.com/v1/product-hut-fe/localizations"
        params = (
            ("location", f"{lng},{lat}"),
            ("order_type", "C"),
            ("limit", "1000"),
            ("openingHour", "1"),
        )

        stores_req = self.__http.get(search_url, headers=headers, params=params)
        try:
            stores = json.loads(stores_req.text)["data"]["items"]
            for store in stores:
                locator_domain = website
                location_name = store["name"]
                log.info(location_name)
                raw_address = store["address"]
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                city = formatted_addr.city
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "NZ"
                store_number = store["code"]
                page_url = f"https://pizzahut.co.nz/huts/{store_number}-{location_name}"

                phone = store.get("phone", "<MISSING>")

                location_type = "<MISSING>"

                hours_of_operation = "<MISSING>"
                try:
                    hours_of_operation = (
                        store["opening_hours"][0]["opening"]
                        + " - "
                        + store["opening_hours"][0]["closing"]
                    )
                except:
                    pass
                latitude = store["lat"]
                longitude = store["long"]
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
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests() as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=["NZ"],
            )

            for rec in par_search.run():
                writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
