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
from sgzip.dynamic import Grain_8, SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import lxml.html

website = "park1.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "manageparking.citizensparking.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://manageparking.citizensparking.com/FindParking/MainFindParkingResult",
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
        params = (
            ("searchPlaceLat", lat),
            ("searchPlaceLng", lng),
            ("latNorthEast", lat),
            ("lngNorthEast", lng),
            ("latSouthWest", lat),
            ("lngSouthWest", lng),
        )

        api_url = "https://manageparking.citizensparking.com/FindParking/FindParkers"
        api_res = self.__http.get(api_url, headers=headers, params=params)

        try:
            stores_sel = lxml.html.fromstring(api_res.text)
            store_list = stores_sel.xpath('//input[@class="json-parker"]')

            for store in store_list:

                page_url = "https://manageparking.citizensparking.com/FindParking/MainFindParkingResult"
                store_json = json.loads(
                    "".join(store.xpath("@value"))
                    .strip()
                    .replace("&quot;", '"')
                    .strip()
                )
                locator_domain = website

                street_address = store_json["Address"].split("(")[0].strip()
                if "," == street_address[-1]:
                    street_address = "".join(street_address[:-1]).strip()

                city = store_json["City"]
                state = store_json["State"]
                zip = store_json["ZIP"]

                if street_address == "6200 HOLLYWOOD BLVD HOLLYWOOD , CA":
                    street_address = "6200 HOLLYWOOD BLVD"
                    city = "HOLLYWOOD"
                    state = "CA"

                country_code = "US"

                location_name = store_json["Name"]
                log.info(location_name)
                phone = store_json["Phone"]
                if phone:
                    if (
                        not phone.replace("(", "")
                        .replace(")", "")
                        .replace("-", "")
                        .strip()
                        .replace(" ", "")
                        .strip()
                        .isdigit()
                    ):
                        phone = "<MISSING>"

                store_number = store_json["ParkerId"]

                location_type = store_json["SrcParkingIconThumbnail"]
                if location_type:
                    location_type = (
                        location_type.replace("../Images/Images/", "")
                        .strip()
                        .replace("-thumbnail.png", "")
                        .strip()
                    )

                hours_of_operation = "<MISSING>"

                latitude, longitude = (
                    store_json["Lat"],
                    store_json["Lng"],
                )
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
        expected_search_radius_miles=100,
        granularity=Grain_8(),
    )

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404]), proxy_country="us") as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=[SearchableCountries.USA],
            )

            for rec in par_search.run():
                writer.write_row(rec)


if __name__ == "__main__":
    scrape()
