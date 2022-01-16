from typing import Iterable, Tuple, Callable
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_2
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
            numbers = "21%2C20"
            nCA = "93%2C91%2C90"
            nUS = "8%2C10%2C28%2C29%2C50"
            nAU = "20"
            if current_country == "ca":
                numbers = nCA
            elif current_country == "us":
                numbers = nUS
            elif current_country == "au":
                numbers = nAU

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
    search_maker = DynamicSearchMaker(
        search_type="DynamicGeoSearch",
        granularity=Grain_2(),
        expected_search_radius_miles=2,
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                },
                fail_on_empty_id=True,
            )
        )
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
