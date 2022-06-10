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
import lxml.html

website = "takko.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.takko.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "origin": "https://www.takko.com",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
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
        params = {
            "dwfrm_storelocator_latitude": lat,
            "dwfrm_storelocator_longitude": lng,
            "dwfrm_storelocator_country": self.__country_name,
            "dwfrm_storelocator_address": "*",
            "dwfrm_storelocator_radius": "50",
        }
        stores_req = self.__http.post(
            "https://www.takko.com/en/stores/", headers=headers, params=params
        )
        json_str = (
            stores_req.text.split("pageContext.stores = ")[1]
            .strip()
            .split("</script>")[0]
            .strip()[:-1]
        )
        stores = json.loads(json_str)

        for store in stores:
            store_number = store["ID"]
            locator_domain = website
            location_name = store["name"]
            street_address = store["address1"]
            if store["address2"] is not None and len(store["address2"]) > 0:
                street_address = street_address + ", " + store["address2"]

            city = store["city"]
            state = "<MISSING>"
            zip = store["postalCode"]
            country_code = store["countryCode"]

            phone = store.get("phone", "<MISSING>")
            if phone:
                phone = phone.replace("+", "").strip()

            location_type = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]
            found_location_at(latitude, longitude)

            hours_of_operation = "<MISSING>"
            hours_list = []
            try:
                hours_sel = lxml.html.fromstring(store["storeHours"])
                hours = hours_sel.xpath("//p")
                for hour in hours:
                    day = "".join(hour.xpath("strong/text()")).strip()
                    time = "".join(hour.xpath("text()")).strip()
                    hours_list.append(day + ":" + time)
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
            )


def scrape():
    log.info("Started")
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        expected_search_radius_miles=50,
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404])) as http:
            countries_req = http.get("https://www.takko.com/en/stores/")
            countries_sel = lxml.html.fromstring(countries_req.text)
            countries = countries_sel.xpath(
                '//select[@id="dwfrm_storelocator_country"]/option/@value'
            )
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
