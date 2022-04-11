# -*- coding: utf-8 -*-
from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration

website = "howdens-cuisines.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.howdens-cuisines.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "accept": "text/html, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.howdens-cuisines.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.howdens-cuisines.com/nos-depots/",
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
        log.info(f"fetching data for coordinates:{lat},{lng}")
        data = {"latitude": lat, "longitude": lng}

        api_url = (
            "https://www.howdens-cuisines.com/wp-content/themes/houdan/ajax-depots.php"
        )

        api_res = self.__http.post(api_url, headers=headers, data=data)

        try:
            stores = api_res.text.split("var marker")[2:]

            for no, store in enumerate(stores, 1):

                store_html = (
                    store.split('("#list_point_retrait").append(\'')[1]
                    .split("</li>")[0]
                    .strip()
                    + "</li>"
                )

                store_sel = lxml.html.fromstring(store_html)

                locator_domain = website
                store_number = "<MISSING>"

                page_url = "https://www.howdens-cuisines.com/nos-depots/"
                location_name = (
                    "".join(store_sel.xpath('//span[@class="name"]//text()'))
                    .strip()
                    .split("(")[0]
                    .strip()
                )
                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath('//span[@class="adress"]//text()')
                        ],
                    )
                )

                phone = (
                    "".join(store_sel.xpath('//span[@class="tel"]//text()'))
                    .strip()
                    .split(":")[1]
                    .strip()
                )

                raw_address = ", ".join(store_info).strip()

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                city = formatted_addr.city

                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "FR"

                hours_of_operation = "<MISSING>"

                latitude, longitude = (
                    store.split("LatLng(")[1].split(")")[0].split(",")[0],
                    store.split("LatLng(")[1].split(")")[0].split(",")[1],
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
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch", expected_search_radius_miles=100
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404])) as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=[SearchableCountries.FRANCE],
            )

            for rec in par_search.run():
                writer.write_row(rec)

    log.info("Finished")


if __name__ == "__main__":
    scrape()
