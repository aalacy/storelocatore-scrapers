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


website = "fiat.at"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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
        self.__country_dict = {
            "at": "3103",
            "be": "3104",
            "cz": "9998",
            "dk": "3107",
            "fr": "3109",
            "de": "3110",
            "gr": "3113",
            "hu": "3129",
            "ie": "3114",
            "it": "1000",
            "lu": "9999",
            "no": "3671",
            "nl": "3122",
            "pl": "3123",
            "pt": "3124",
            "sk": "9997",
            "es": "3136",
            "ch": "3128",
            "za": "3353",
            "bw": "3353",
        }

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
        search_url = "https://dealerlocator.fiat.com/geocall/RestServlet?jsonp=callback&mkt={}&brand=00&func=finddealerxml&serv=sales&track=1&x={}&y={}&rad=100"
        mkt = self.__country_dict[self.__country_name]
        stores_req = self.__http.get(search_url.format(mkt, lng, lat), headers=headers)

        try:
            json_str = (
                stores_req.text.split("callback(")[1].strip().split("})")[0].strip()
                + "}"
            )
            if "results" in json_str:

                for store in json.loads(json_str)["results"]:
                    page_url = store.get("WEBSITE", "<MISSING>")
                    locator_domain = website
                    location_name = store["COMPANYNAM"]
                    street_address = store["ADDRESS"]
                    city = store["TOWN"]
                    state = store["PROVINCE"]
                    if state and state.isdigit():
                        state = "<MISSING>"

                    zip = store["ZIPCODE"]
                    country_code = self.__country_name
                    store_number = store["MAINCODE"]
                    phone = store["TEL_1"]
                    location_type = store["BUSINESS_CENTER"]
                    if location_type == 1:
                        location_type = "BUSINESS_CENTER"
                    else:
                        location_type = "<MISSING>"

                    hours_list = []
                    try:
                        hours = store["ACTIVITY"][0]
                        for key in hours.keys():
                            if "OPENTIME" in key:
                                day = hours[key]["DATEWEEK"]
                                if (
                                    "MORNING_FROM" in hours[key]
                                    and "AFTERNOON_TO" in hours[key]
                                ):
                                    time = (
                                        hours[key]["MORNING_FROM"]
                                        + " - "
                                        + hours[key]["AFTERNOON_TO"]
                                    )
                                elif (
                                    "MORNING_FROM" in hours[key]
                                    and "MORNING_TO" in hours[key]
                                ):
                                    time = (
                                        hours[key]["MORNING_FROM"]
                                        + " - "
                                        + hours[key]["MORNING_TO"]
                                    )
                                elif (
                                    "AFTERNOON_FROM" in hours[key]
                                    and "AFTERNOON_TO" in hours[key]
                                ):
                                    time = (
                                        hours[key]["AFTERNOON_FROM"]
                                        + " - "
                                        + hours[key]["AFTERNOON_TO"]
                                    )
                                else:
                                    time = "Closed"

                                hours_list.append(day + ":" + time)
                    except:
                        pass

                    hours_of_operation = "; ".join(hours_list).strip()
                    latitude = store["YCOORD"]
                    longitude = store["XCOORD"]

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
            log.error(self.__country_name)
            pass


def scrape():
    log.info("Started")
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=20,
    )

    country_list = [
        "at",
        "be",
        "cz",
        "dk",
        "fr",
        "de",
        "gr",
        "hu",
        "ie",
        "it",
        "lu",
        "no",
        "nl",
        "pl",
        "pt",
        "sk",
        "es",
        "ch",
        "za",
        "bw",
    ]

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for country in country_list:

            with SgRequests(dont_retry_status_codes=([404])) as http:
                search_iter = _SearchIteration(http=http, country=country)
                par_search = ParallelDynamicSearch(
                    search_maker=search_maker,
                    search_iteration=search_iter,
                    country_codes=[country],
                )

                for rec in par_search.run():
                    writer.write_row(rec)


if __name__ == "__main__":
    scrape()
