from typing import Iterable, Tuple, Callable
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "giantfood.com/pharmacy"
log = sglog.SgLogSetup().get_logger(logger_name=website)


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

        log.info(f"pulling data for zipcode: {zipcode}")
        headers = {
            "authority": "api-cs.rxtouch.com",
            "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            "x-contactid": "",
            "x-sessionid": "",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "content-type": "application/json",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-productionlevel": "0",
            "sec-ch-ua-platform": '"Windows"',
            "origin": "https://giantfoodweb.rxtouch.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://giantfoodweb.rxtouch.com/",
            "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
        }

        try:
            payload = {"vcZIPCode": zipcode, "vcLocale": "en-US"}

            r = self.__http.post(
                "https://api-cs.rxtouch.com/rxwebapi/1.0.8/giantfood/api/Store/GetStoresByZip",
                headers=headers,
                data=json.dumps(payload),
            )

            json_data = r.json()
            if json_data["success"] is True:

                for data in json_data["data"]:
                    locator_domain = website
                    location_name = data["nvcStoreName"]
                    street_address = data["nvcAddress1"]

                    if data["nvcAddress2"]:
                        street_address += ", " + data["nvcAddress2"]
                    city = data["nvcCity"]
                    state = data["nvcState"]
                    zip = data["vcZip"]
                    location_type = "<MISSING>"
                    phone = data["vcPharmacyPhone"]
                    country_code = "US"
                    latitude = data["fLatitude"]
                    longitude = data["fLongitude"]
                    found_location_at(float(latitude), float(longitude))
                    hours = ""
                    try:
                        details = data["Details"]
                        for d in details:
                            if "Pharmacy Hours" == d["nvcTitle"]:
                                hours = d["nvcDescription"].replace("\n", "; ").strip()
                                if hours:
                                    if ";" == hours[-1]:
                                        hours = "".join(hours[:-1]).strip()
                                break
                    except:
                        pass

                    page_url = "https://giantfood.com/pharmacy"
                    store_number = data["iStoreID"]

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
                        hours_of_operation=hours,
                    )

        except:
            pass


def scrape():
    log.info("Started")
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicZipSearch",
        expected_search_radius_miles=100,
    )

    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests(dont_retry_status_codes=([404])) as http:
            search_iter = _SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=["US"],
            )

            for rec in par_search.run():
                writer.write_row(rec)


if __name__ == "__main__":
    scrape()
