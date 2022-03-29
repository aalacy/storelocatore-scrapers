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
from sgpostal import sgpostal as parser


website = "alfaromeo.se"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.alfaromeo.se",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
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
        # country=> key, language:domain_part => value
        self.__country_dict = {
            "az": "en:.az",
            "il": "he:.co.il",
            "bg": "en:.bg",
            "cy": "en:.com.cy",
            "ee": "en:.ee",
            "fi": "en:.fi",
            "lv": "lv:.lv",
            "lt": "en:-official.lt",
            "mt": "mt:.com.mt",
            "mk": "en:.mk",
            "ro": "en:.ro",
            "se": "sv:.se",
            "re": "fr:.re",
            "ua": "en:.ua",
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
            f"fetching data for country: {current_country} having coordinates:{lat},{lng}"
        )
        search_url = "https://www.alfaromeo{}/wp-content/themes/fca-themes-alfa/js/json/stores.php?lat={}&lng={}&current_language_code={}&distance=100"
        current_language_code = (
            self.__country_dict[current_country].split(":")[0].strip()
        )
        domain_part = self.__country_dict[current_country].split(":")[-1].strip()

        final_url = search_url.format(domain_part, lat, lng, current_language_code)

        stores_req = self.__http.get(
            final_url,
            headers=headers,
        )
        try:
            if "data" in stores_req.text:

                for store in json.loads(stores_req.text)["data"]:
                    page_url = "<MISSING>"
                    locator_domain = website
                    location_name = store["name"]
                    raw_address = store["address"]
                    if raw_address:
                        raw_address = raw_address.replace("\n", "").strip()
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if street_address:
                        if formatted_addr.street_address_2:
                            street_address = (
                                street_address + ", " + formatted_addr.street_address_2
                            )
                    else:
                        if formatted_addr.street_address_2:
                            street_address = formatted_addr.street_address_2

                    city = formatted_addr.city
                    state = formatted_addr.state
                    zip = formatted_addr.postcode

                    country_code = current_country
                    store_number = store["id"]
                    phone = (
                        store["dealer_phone"]
                        .replace("Showroom:", "")
                        .strip()
                        .replace("Showroom/", "")
                        .strip()
                        .split("Service:")[0]
                        .strip()
                        .replace("Pardavimai:", "")
                        .strip()
                        .split(";<br>Servisas:")[0]
                        .strip()
                        .replace("Pardavimai/Servisas:", "")
                        .strip()
                        .replace("Продажби:</br>", "")
                        .strip()
                        .replace("Automüük/Teenindus:", "")
                        .strip()
                        .split(";<br>  Servisas:")[0]
                        .strip()
                        .split(";<br>Serviss:")[0]
                        .strip()
                        .replace("Pārdošana:", "")
                        .strip()
                        .replace("Auto San Marino - Bistrita Nasaud", "")
                        .strip()
                    )
                    location_type = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    latitude = store["lat"]
                    longitude = store["lng"]

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
        expected_search_radius_miles=50,
    )

    country_list = [
        "az",
        "il",
        "bg",
        "cy",
        "ee",
        "fi",
        "lv",
        "lt",
        "mt",
        "mk",
        "ro",
        "se",
        "re",
        "ua",
    ]

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404])) as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=country_list,
            )

            for rec in par_search.run():
                writer.write_row(rec)


if __name__ == "__main__":
    scrape()
