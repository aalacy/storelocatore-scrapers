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


def strip_para(x):
    copy = []
    inside = False
    for i in x:
        if i == "<" or inside:
            inside = True
            continue
        elif i == ">":
            inside = False
            continue
        else:
            copy.append(i)
    return "".join(copy)


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def replac(x):
    x = str(x)
    x = x.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
    if len(x) < 1:
        return "<MISSING>"
    return x


class ExampleSearchIteration(SearchIteration):
    """
    Here, you define what happens with each iteration of the search.
    The `do(...)` method is what you'd do inside of the `for location in search:` loop
    It provides you with all the data you could get from the search instance, as well as
    a method to register found locations.
    """

    def __init__(self):
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
        with SgRequests() as http:
            # here you'd use self.__http, and call `found_location_at(lat, long)` for all records you find.
            lat, lng = coord
            # just some clever accounting of locations/country:
            numbers = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99"
            url = str(
                f"https://marketingsl.tjx.com/storelocator/GetSearchResults?geolat={lat}&geolong={lng}&chain={numbers}&maxstores=9999&radius=1000"
            )
            headers = {}
            headers[
                "user-agent"
            ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            locations = None
            try:
                locations = SgRequests.raise_on_err(
                    http.get(url, headers=headers)
                ).json()
            except Exception as e:
                logzilla.error(f"{e}")
            MISSING = "<MISSING>"
            if locations:
                if locations["Status"] == 0:
                    for rec in locations["Stores"]:
                        location_name = str(
                            str(rec["Name"]).strip(),
                        )
                        street_address = str(
                            str(rec["Address"]).strip()
                            + ", "
                            + str(rec["Address2"]).strip(),
                        )
                        city = str(
                            str(rec["City"]).strip(),
                        )
                        state = str(
                            str(rec["State"]).strip(),
                        )
                        zip_postal = str(
                            str(rec["Zip"]).strip(),
                        )
                        country_code = str(
                            str(rec["Country"]).strip(),
                        )
                        store_number = str(
                            str(rec["StoreID"]).strip(),
                        )
                        phone = str(
                            str(rec["Phone"]).strip(),
                        )
                        location_type = str(
                            str(rec["Chain"]).strip(),
                        )
                        latitude = str(
                            rec["Latitude"],
                        )
                        longitude = str(
                            rec["Longitude"],
                        )
                        hours_of_operation = str(
                            strip_para(str(rec["Hours"])).strip(),
                        )
                        if latitude:
                            if longitude:
                                found_location_at(
                                    replac(str(latitude)), replac(str(longitude))
                                )
                        yield SgRecord(
                            page_url=MISSING,
                            location_name=replac(location_name)
                            if location_name
                            else MISSING,
                            street_address=replac(fix_comma(street_address))
                            if street_address
                            else MISSING,
                            city=replac(city) if city else MISSING,
                            state=replac(state) if state else MISSING,
                            zip_postal=replac(zip_postal) if zip_postal else MISSING,
                            country_code=replac(country_code)
                            if country_code
                            else MISSING,
                            store_number=replac(store_number)
                            if store_number
                            else MISSING,
                            phone=replac(phone) if phone else MISSING,
                            location_type=replac(location_type)
                            if location_type
                            else MISSING,
                            latitude=replac(latitude) if latitude else MISSING,
                            longitude=replac(longitude) if longitude else MISSING,
                            locator_domain=MISSING,
                            hours_of_operation=replac(hours_of_operation)
                            if hours_of_operation
                            else MISSING,
                            raw_address=MISSING,
                        )


if __name__ == "__main__":
    tocrawl = []
    tocrawl.append(SearchableCountries.USA)
    tocrawl.append(SearchableCountries.CANADA)
    tocrawl.append(SearchableCountries.AUSTRALIA)
    tocrawl = tocrawl + SearchableCountries.ByGeography["CONTINENTAL_EUROPE"]
    # additionally to 'search_type', 'DynamicSearchMaker' has all options that all `DynamicXSearch` classes have.
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        granularity=Grain_8(),
        expected_search_radius_miles=100,
    )

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)
    ) as writer:
        with SgRequests() as http1:
            search_iter = ExampleSearchIteration()
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=tocrawl,
            )

            for rec in par_search.run():
                writer.write_row(rec)
