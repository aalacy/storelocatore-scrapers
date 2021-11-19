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
import json
from bs4 import BeautifulSoup as b4

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

            url = str(
                f"https://locator-svc.subway.com/v3/GetLocations.ashx?callback=jQuery111103111319300901092_1617727334311&q=%7B%22InputText%22%3A%22%22%2C%22GeoCode%22%3A%7B%22name%22%3A%22%22%2C%22Latitude%22%3A{lat}%2C%22Longitude%22%3A{lng}%2C%22CountryCode%22%3A%22%22%7D%2C%22DetectedLocation%22%3A%7B%22Latitude%22%3A0%2C%22Longitude%22%3A0%2C%22Accuracy%22%3A0%7D%2C%22Paging%22%3A%7B%22StartIndex%22%3A0%2C%22PageSize%22%3A100%7D%2C%22ConsumerParameters%22%3A%7B%22metric%22%3Atrue%2C%22culture%22%3A%22en-AG%22%2C%22country%22%3A%22%22%2C%22size%22%3A%22D%22%2C%22template%22%3A%22%22%2C%22rtl%22%3Afalse%2C%22clientId%22%3A%2217%22%2C%22key%22%3A%22SUBWAY_PROD%22%7D%2C%22Filters%22%3A%5B%5D%2C%22LocationType%22%3A2%2C%22behavior%22%3A%22%22%2C%22FavoriteStores%22%3Anull%2C%22RecentStores%22%3Anull%2C%22Stats%22%3A%7B%22abc%22%3A%5B%7B%22N%22%3A%22geo%22%2C%22R%22%3A%22B%22%7D%5D%2C%22src%22%3A%22autocomplete%22%2C%22act%22%3A%22enter%22%2C%22c%22%3A%22subwayLocator%22%7D%7D&_=1617727334313".format(lat=lat,lng=lng)
                )
            headers = {}
            headers[
                "user-agent"
            ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            locations = None
            try:
                locations = SgRequests.raise_on_err(
                    http.get(url, headers=headers)
                ).text
                locations = locations.split("(",1)[1]
                locations = locations.rsplit(")",1)[0]
                locations = json.loads(locations)
            except Exception as e:
                logzilla.error(f"{e}")
            MISSING = "<MISSING>"
            if locations:
                firstfound = set()
                secondfound = set()
                foundstuff = {}
                for rec in locations["ResultData"]:
                    try:
                        page_url = rec["OrderingUrl"]
                    except Exception:
                        page_url = None

                    try:
                        street_address = rec["Address"]["Address1"]+", "+rec["Address"]["Address2"]+", "+rec["Address"]["Address3"]
                    except Exception:
                        street_address = None

                    try:
                        city = rec["Address"]["City"]
                    except Exception:
                        city = None

                    try:
                        state = rec["Address"]["StateProvCode"]
                    except Exception:
                        state = None

                    try:
                        country_code = rec["Address"]["CountryCode"]
                    except Exception:
                        country_code = None

                    try:
                        zip_postal = rec["Address"]["PostalCode"]
                    except Exception:
                        zip_postal = None

                    try:
                        store_number = str(rec["LocationId"]["StoreNumber"]) + "-" + str(rec["LocationId"]["SatelliteNumber"])
                    except Exception:
                        store_number = None

                    try:
                        longitude = rec["Geo"]["Longitude"]
                    except Exception:
                        longitude = None

                    try:
                        latitude = rec["Geo"]["Latitude"]
                    except Exception:
                        latitude = None


                    current = {
                            "page_url":page_url if page_url else MISSING,
                            "location_name":MISSING,
                            "street_address":street_address if street_address else MISSING,
                            "city":city if city else MISSING,
                            "state":state if state else MISSING,
                            "zip_postal":zip_postal if zip_postal else MISSING,
                            "country_code":country_code
                            if country_code
                            else MISSING,
                            "store_number":store_number
                            if store_number
                            else MISSING,
                            "phone":MISSING,
                            "location_type":MISSING,
                            "latitude":latitude if latitude else MISSING,
                            "longitude":longitude if longitude else MISSING,
                            "locator_domain":"subway.com",
                            "hours_of_operation":MISSING,
                            "raw_address":MISSING,
                        }
                    foundstuff[current["store_number"]]=current
                    firstfound.add(current["store_number"])
                    found_location_at(latitude,longitude)
                i = 0
                for html in locations["ResultHtml"]:
                    print("Helloooo")
                    soup = b4(html,"lxml")
                    i+= 1
                    if len(html)<50:
                        continue
                    hours = " ".join(
            list(
                soup.find(
                    "div", {"class": lambda x: x and "hoursTable" in x}
                ).stripped_strings
            )
        )

                    storeno = soup.find("div",{"class":"location"})["data-id"]
                    phone = soup.find("div",{"class": "locatorPhone"}).text
                    foundstuff[storeno]["phone"]=phone if phone else MISSING
                    foundstuff[storeno]["hours_of_operation"]=hours if hours else MISSING
                    secondfound.add(storeno)
                    yield SgRecord(
                        page_url=foundstuff[storeno]["page_url"],
                        location_name=foundstuff[storeno]["location_name"],
                        street_address=foundstuff[storeno]["street_address"],
                        city=foundstuff[storeno]["city"],
                        state=foundstuff[storeno]["state"],
                        zip_postal=foundstuff[storeno]["zip_postal"],
                        country_code=foundstuff[storeno]["country_code"],
                        store_number=foundstuff[storeno]["store_number"],
                        phone=foundstuff[storeno]["phone"],
                        location_type=foundstuff[storeno]["location_type"],
                        latitude=foundstuff[storeno]["latitude"],
                        longitude=foundstuff[storeno]["longitude"],
                        locator_domain=foundstuff[storeno]["locator_domain"],
                        hours_of_operation=foundstuff[storeno]["hours_of_operation"],
                        raw_address=foundstuff[storeno]["raw_address"],
                    )
            this = []
            this = list(firstfound.symmetric_difference(secondfound))
            if len(this)>0 :
                for storenum in this:
                    yield SgRecord(
                        page_url=foundstuff[storenum]["page_url"],
                        location_name=foundstuff[storenum]["location_name"],
                        street_address=foundstuff[storenum]["street_address"],
                        city=foundstuff[storenum]["city"],
                        state=foundstuff[storenum]["state"],
                        zip_postal=foundstuff[storenum]["zip_postal"],
                        country_code=foundstuff[storenum]["country_code"],
                        store_number=foundstuff[storenum]["store_number"],
                        phone=foundstuff[storenum]["phone"],
                        location_type=foundstuff[storenum]["location_type"],
                        latitude=foundstuff[storenum]["latitude"],
                        longitude=foundstuff[storenum]["longitude"],
                        locator_domain=foundstuff[storenum]["locator_domain"],
                        hours_of_operation=foundstuff[storenum]["hours_of_operation"],
                        raw_address=foundstuff[storenum]["raw_address"],
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
        with SgRequests() as http1:
            search_iter = ExampleSearchIteration()
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
            )
            for rec in par_search.run():
                writer.write_row(rec)
