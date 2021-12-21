# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration


website = "postoffice.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.postoffice.co.uk",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.postoffice.co.uk",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.postoffice.co.uk/branch-finder",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
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
        data = {"searchString": f"{lat}|{lng}|locality", "productSelections": []}
        api_url = "https://www.postoffice.co.uk/.rest/branch-finder/ep/branchBylatlng"
        api_res = self.__http.post(api_url, headers=headers, data=json.dumps(data))

        try:
            json_res = json.loads(api_res.text)

            store_list = json_res["responseBody"]["branchList"]

            for store in store_list:

                page_url = (
                    "https://www.postoffice.co.uk/branch-finder/"
                    + store["fadCode"]
                    + "/"
                    + store["name"].lower().replace(" ", "-").strip()
                )

                locator_domain = website

                raw_address = store["address"].strip()

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    if street_address:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )
                    else:
                        street_address = formatted_addr.street_address_2

                if street_address:
                    if street_address.replace("-", "").strip().isdigit():
                        try:
                            street_address = raw_address.split(",")[0].strip()
                        except:
                            pass

                try:
                    street_address = ", ".join(raw_address.split(",")[:2]).strip()
                except:
                    pass
                city = formatted_addr.city
                state = formatted_addr.state
                zip = store["postCode"].strip()

                country_code = "GB"

                location_name = store["name"].strip()
                if not city:
                    city = location_name

                phone = "<MISSING>"
                store_number = store["id"]

                location_type = "<MISSING>"

                hours = store["openingTiming"]
                hour_list = []
                for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                    if (val := hours[day]["regular"]) :
                        hour_list.append(f"{day}: {val}")
                    else:
                        hour_list.append(f"{day}: Closed")

                hours_of_operation = "; ".join(hour_list)

                latitude, longitude = (
                    store["location"]["latitude"],
                    store["location"]["longitude"],
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
        expected_search_radius_miles=100,
        granularity=Grain_8(),
    )

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        with SgRequests(dont_retry_status_codes=([404])) as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=["GB"],
            )

            for rec in par_search.run():
                writer.write_row(rec)


if __name__ == "__main__":
    scrape()
