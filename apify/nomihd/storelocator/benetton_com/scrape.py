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

website = "benetton.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "api.woosmap.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "accept": "*/*",
    "origin": "https://us.benetton.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


class _SearchIteration(SearchIteration):
    """
    Here, you define what happens with each iteration of the search.
    The `do(...)` method is what you'd do inside of the `for location in search:` loop
    It provides you with all the data you could get from the search instance, as well as
    a method to register found locations.
    """

    def __init__(self, http: SgRequests, country: str):
        self.__http = http
        self.__state = CrawlStateSingleton.get_instance()
        self.__country_name = country
        session = SgRequests()
        search_url = "https://us.benetton.com/store-locator"
        stores_req = session.get(search_url)
        self.__API_KEY = (
            stores_req.text.split('data-publicKey="')[1].strip().split('"')[0].strip()
        )

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
        log.info(
            f"fetching data for country: {self.__country_name} having coordinates:{lat},{lng}"
        )
        params = (
            ("key", self.__API_KEY),
            ("lat", lat),
            ("lng", lng),
            ("max_distance", "25000"),
            ("stores_by_page", "40"),
            ("limit", "40"),
            ("page", "1"),
        )
        stores_req = self.__http.get(
            "https://api.woosmap.com/stores/search", headers=headers, params=params
        )
        stores = json.loads(stores_req.text)["features"]
        for store in stores:
            prop = store["properties"]
            store_number = prop["store_id"]
            locator_domain = website
            location_name = prop["name"]
            raw_address = ""
            street_address = ", ".join(prop["address"]["lines"]).strip()
            if street_address:
                raw_address = street_address

            city = prop["address"]["city"]
            if city:
                raw_address = raw_address + ", " + city

            state = "<MISSING>"
            zip = prop["address"]["zipcode"]
            if zip:
                if zip == "." or zip == "-":
                    zip = "<MISSING>"
                else:
                    raw_address = raw_address + ", " + zip

            country_code = prop["address"]["country_code"]

            phone = prop["contact"]["phone"]
            if not phone:
                phone = "<MISSING>"

            if phone and phone == "null":
                phone = "<MISSING>"

            location_type = "<MISSING>"

            latitude = store["geometry"]["coordinates"][1]
            longitude = store["geometry"]["coordinates"][0]
            found_location_at(latitude, longitude)

            hours_of_operation = "<MISSING>"
            hours_list = []
            try:
                hours = prop["opening_hours"]["usual"]  # mon-sun
                for day_val in hours.keys():
                    day = ""
                    if day_val == "1":
                        day = "Monday:"
                    if day_val == "2":
                        day = "Tuesday:"
                    if day_val == "3":
                        day = "Wednesday:"
                    if day_val == "4":
                        day = "Thursday:"
                    if day_val == "5":
                        day = "Friday:"
                    if day_val == "6":
                        day = "Saturday:"
                    if day_val == "7":
                        day = "Sunday:"

                    start = hours[day_val][0]["start"]
                    end = hours[day_val][0]["end"]
                    time = start + " - " + end
                    hours_list.append(day + time)
            except:
                pass

            hours_of_operation = "; ".join(hours_list).strip()
            page_url = "<MISSING>"
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


def scrape():
    log.info("Started")
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=20,
    )
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404])) as http:
            countries = SearchableCountries.ALL
            for country in countries:
                search_iter = _SearchIteration(http=http, country=country)
                par_search = ParallelDynamicSearch(
                    search_maker=search_maker,
                    search_iteration=search_iter,
                    country_codes=[country],
                )

                for rec in par_search.run():
                    writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
