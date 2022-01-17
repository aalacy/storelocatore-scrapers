from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_8
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration
from sglogging import sglog

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


class ExampleSearchIteration(SearchIteration):
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
        """
        This method gets called on each iteration of the search.
        It provides you with all the data you could get from the search instance, as well as
        a method to register found locations.

        :param coord: The current coordinate (lat, long)
        :param zipcode: The current zipcode (In DynamicGeoSearch instances, please ignore!)
        :param current_country: The current country (don't assume continuity between calls - it's meant to be parallelized)
        :param items_remaining: Items remaining in the search - per country, if `ParallelDynamicSearch` is used.
        :param found_location_at: The equivalent of `search.found_location_at(lat, long)`
        """

        # here you'd use self.__http, and call `found_location_at(lat, long)` for all records you find.
        lat, lng = coord
        # just some clever accounting of locations/country:
        url = str(
            "https://www.choicehotels.com/webapi/location/hotels?adults=1&checkInDate=3022-05-19&checkOutDate=3022-05-20&hotelSortOrder=RELEVANCE&include=amenity_groups%2C%20amenity_totals%2C%20rating%2C%20relative_media%2C%20renovation_info%2C%20awards_info"
            + f"&lat={lat}&lon={lng}&"
            + "optimizeResponse=image_url&placeId=404698&platformType=DESKTOP&preferredLocaleCode=en-us&ratePlans=RACK%2CPREPD%2CPROMO%2CFENCD&rateType=LOW_ALL&rooms=1&searchRadius=100&siteName=us&siteOpRelevanceSortMethod=ALGORITHM_B"
        )
        headers = {}
        headers[
            "accept"
        ] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        headers["accept-encoding"] = "gzip, deflate, br"
        headers["accept-language"] = "en-US,en;q=0.9"
        headers["cache-control"] = "no-cache"
        headers["pragma"] = "no-cache"
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        try:
            locations = SgRequests.raise_on_err(http.get(url, headers=headers)).json()
            errorName = None
        except Exception as e:
            logzilla.error(f"{e} , {url}<-F")
            locations = {"hotelCount": 0}
            locations["status"] = "FAIL"
            errorName = str(e)
        if (
            locations["status"] == "OK"
            and locations["hotelCount"] > 0
            and "NONEXISTENT_HOTEL_INFO" not in str(locations)
        ):
            for record in locations["hotels"]:
                try:
                    record["address"]["subdivision"] = record["address"]["subdivision"]
                except KeyError:
                    record["address"]["subdivision"] = SgRecord.MISSING
                try:
                    record["name"] = record["name"]
                except KeyError:
                    record["name"] = SgRecord.MISSING

                try:
                    record["phone"] = record["phone"]
                except KeyError:
                    record["phone"] = SgRecord.MISSING

                try:
                    record["brandCode"] = record["brandCode"]
                except KeyError:
                    record["brandCode"] = SgRecord.MISSING

                try:
                    record["brandName"] = record["brandName"]
                except KeyError:
                    record["brandName"] = SgRecord.MISSING

                try:
                    record["lon"] = record["lon"]
                except KeyError:
                    record["lon"] = SgRecord.MISSING

                try:
                    record["lat"] = record["lat"]
                    found_location_at(record["lat"], record["lon"])
                except KeyError:
                    record["lat"] = SgRecord.MISSING

                try:
                    record["address"]["line1"] = record["address"]["line1"]
                except KeyError:
                    record["address"]["line1"] = SgRecord.MISSING
                try:
                    record["address"]["city"] = record["address"]["city"]
                except KeyError:
                    record["address"]["city"] = SgRecord.MISSING
                try:
                    record["address"]["postalCode"] = record["address"]["postalCode"]
                except KeyError:
                    record["address"]["postalCode"] = SgRecord.MISSING
                try:
                    record["address"]["country"] = record["address"]["country"]
                except KeyError:
                    record["address"]["country"] = SgRecord.MISSING

                try:
                    yield SgRecord(
                        page_url="https://www.choicehotels.com/" + str(record["id"]),
                        location_name=str(record["name"]),
                        street_address=str(record["address"]["line1"]),
                        city=str(record["address"]["city"]),
                        state=str(record["address"]["subdivision"]),
                        zip_postal=str(record["address"]["postalCode"]),
                        country_code=str(record["address"]["country"]),
                        store_number=str(record["id"]),
                        phone=str(record["phone"]),
                        location_type=str(
                            str(record["brandCode"]) + " - " + str(record["brandName"])
                        ),
                        latitude=str(record["lat"]),
                        longitude=str(record["lon"]),
                        locator_domain="https://www.choicehotels.com/",
                        hours_of_operation=SgRecord.MISSING,
                        raw_address=errorName if errorName else SgRecord.MISSING,
                    )
                except KeyError:
                    yield SgRecord(
                        page_url=SgRecord.MISSING,
                        location_name=SgRecord.MISSING,
                        street_address=SgRecord.MISSING,
                        city=SgRecord.MISSING,
                        state=SgRecord.MISSING,
                        zip_postal=SgRecord.MISSING,
                        country_code=SgRecord.MISSING,
                        store_number=str(record["id"]),
                        phone=SgRecord.MISSING,
                        location_type=SgRecord.MISSING,
                        latitude=SgRecord.MISSING,
                        longitude=SgRecord.MISSING,
                        locator_domain=SgRecord.MISSING,
                        hours_of_operation=SgRecord.MISSING,
                        raw_address=errorName if errorName else str(record),
                    )


if __name__ == "__main__":
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        granularity=Grain_8(),
        expected_search_radius_miles=100,
    )

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)
    ) as writer:
        with SgRequests() as http:
            search_iter = ExampleSearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
            )

            for rec in par_search.run():
                writer.write_row(rec)
