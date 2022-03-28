# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
import json
import lxml.html

website = "saintcinnamonquebec.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "saintcinnamonquebec.ca",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://saintcinnamonquebec.ca/restaurants/",
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
            ("lang", "en"),
            ("action", "store_search"),
            ("lat", lat),
            ("lng", lng),
            ("max_results", "25"),
            ("search_radius", "500"),
            ("autoload", "1"),
        )
        stores_req = self.__http.get(
            "https://saintcinnamonquebec.ca/wp-admin/admin-ajax.php",
            headers=headers,
            params=params,
        )
        stores = json.loads(stores_req.text)

        for store in stores:
            page_url = store["permalink"]
            locator_domain = website
            location_name = store["store"]
            street_address = store["address"]
            if store["address2"] is not None and len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]

            if ",," in street_address:
                street_address = street_address.replace(",,", ",").strip()

            city = store["city"].replace(",", "").strip()
            state = store["state"]
            zip = store["zip"]

            country_code = store["country"]

            store_number = store["id"]
            phone = store["phone"]

            location_type = "<MISSING>"
            hours_list = []
            if store["hours"] is not None and len(store["hours"]) > 0:
                hours = lxml.html.fromstring(store["hours"]).xpath("//tr")
                for hour in hours:
                    day = "".join(hour.xpath("td[1]/text()")).strip()
                    time = "".join(hour.xpath("td[2]//text()")).strip()
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["lat"]
            longitude = store["lng"]

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


def scrape():
    log.info("Started")
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=100,
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.COUNTRY_CODE,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        countries = ["CA", "PH", "ID"]
        for country in countries:
            with SgRequests(dont_retry_status_codes=([404])) as http:
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
