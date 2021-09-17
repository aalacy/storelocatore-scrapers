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
    x = x.replace("None", "")
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

        lat, lng = coord
        url = str(f"https://www.starbucks.com/bff/locations?lat={lat}&lng={lng}")
        headers = {}
        headers["x-requested-with"] = "XMLHttpRequest"
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        try:
            locations = http.get(url, headers=headers).json()
            if locations["paging"]["total"] > 0:
                for record in locations["stores"]:
                    try:
                        try:
                            found_location_at(
                                record["coordinates"]["latitude"],
                                record["coordinates"]["longitude"],
                            )
                        except Exception:
                            pass
                        yield SgRecord(
                            page_url="https://www.starbucks.com/store-locator/store/{}/{}".format(
                                str(record["id"]), str(record["slug"])
                            ),
                            location_name=str(record["name"]),
                            street_address=fix_comma(
                                str(
                                    str(record["address"]["streetAddressLine1"])
                                    + ","
                                    + str(record["address"]["streetAddressLine2"])
                                    + ","
                                    + str(record["address"]["streetAddressLine3"])
                                )
                            ),
                            city=str(record["address"]["city"]),
                            state=str(record["address"]["countrySubdivisionCode"]),
                            zip_postal=str(record["address"]["postalCode"]),
                            country_code=str(record["address"]["countryCode"]),
                            store_number=str(record["id"]),
                            phone=str(record["phoneNumber"]),
                            location_type=str(
                                str(record["brandName"])
                                + " - "
                                + str(record["ownershipTypeCode"])
                            ),
                            latitude=str(record["coordinates"]["latitude"]),
                            longitude=str(record["coordinates"]["longitude"]),
                            locator_domain="https://www.starbuck.com/",
                            hours_of_operation=str(record["schedule"]),
                            raw_address=SgRecord.MISSING,
                        )
                        rec_count = self.__state.get_misc_value(
                            current_country, default_factory=lambda: 0
                        )
                        self.__state.set_misc_value(current_country, rec_count + 1)
                    except KeyError as e:
                        yield SgRecord(
                            page_url=SgRecord.MISSING,
                            location_name=SgRecord.MISSING,
                            street_address=SgRecord.MISSING,
                            city=SgRecord.MISSING,
                            state=SgRecord.MISSING,
                            zip_postal=SgRecord.MISSING,
                            country_code=SgRecord.MISSING,
                            store_number=str(record),
                            phone=SgRecord.MISSING,
                            location_type=SgRecord.MISSING,
                            latitude=SgRecord.MISSING,
                            longitude=SgRecord.MISSING,
                            locator_domain=SgRecord.MISSING,
                            hours_of_operation=SgRecord.MISSING,
                            raw_address=str(e),
                        )
        except Exception as e:
            logzilla.error(f"{e}")
            locations = {"paging": {"total": 0}}
            yield SgRecord(
                page_url=url,
                location_name="<ERROR>",
                street_address="<ERROR>",
                city="<ERROR>",
                state="<ERROR>",
                zip_postal="<ERROR>",
                country_code="<ERROR>",
                phone="<ERROR>",
                location_type="<ERROR>",
                latitude=lat,
                longitude=lng,
                locator_domain="<ERROR>",
                hours_of_operation=str(url),
                raw_address=str(e),
            )


if __name__ == "__main__":
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        granularity=Grain_8(),
        max_search_results=50,
        expected_search_radius_miles=8,
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
