from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, Grain_4, SearchableCountries
from sgzip.utils import country_names_by_code
from fuzzywuzzy import process
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sgscrape.pause_resume import CrawlStateSingleton, CrawlState
from dataclasses import asdict, dataclass
from typing import Iterable, Optional
from sgzip.utils import earth_distance
from ordered_set import OrderedSet
from csv import reader
import json
import time
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")

state = CrawlStateSingleton.get_instance()
headerz = None
@dataclass(frozen=False)
class SerializableCountry:
    """
    Consists of fields that define a country.
    """

    name: str
    code: str
    empty: bool
    tested: bool
    retries: int

    def serialize(self) -> str:
        return json.dumps(asdict(self))

    def __hash__(self):
        return hash((self.name, self.code, self.empty, self.tested, self.retries))

    def __eq__(self, other):
        return isinstance(other, SerializableCountry) and hash(self) == hash(other)

    @staticmethod
    def deserialize(serialized_json: str) -> "SerializableCountry":
        as_dict = json.loads(serialized_json)
        return SerializableCountry(
            name=as_dict["name"],
            code=as_dict["code"],
            empty=as_dict["empty"],
            tested=as_dict["tested"],
            retries=as_dict["retries"],
        )


class CountryStack:
    def __init__(
        self, seed: Optional[OrderedSet[SerializableCountry]], state: "CrawlState"
    ):
        self.__country_stack = seed
        self.__state = state

    def push_country(self, req: SerializableCountry) -> bool:  # type: ignore
        self.__country_stack.add(req)  # type: ignore

    def pop_country(self) -> Optional[SerializableCountry]:
        return self.__country_stack.pop() if self.__country_stack else None

    def serialize_country(self) -> Iterable[str]:  # type: ignore
        return list(map(lambda r: r.serialize(), self.__country_stack))  # type: ignore

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.__country_stack)

    def __next__(self):
        req = self.pop_request()
        return req


def get_special(session, headers, special):
    page = session.get(
        "https://locate.apple.com{}".format(special["link"]), headers=headers
    )
    soup = b4(page.text, "lxml")
    soup = soup.find_all("script", {"type": "text/javascript"})
    theScript = None
    for i in soup:
        if "window.resourceLocator.setup = " in i.text:
            theScript = i.text
    theScript = json.loads(
        str(theScript.split("window.resourceLocator.setup = ", 1)[1].split("};", 1)[0])
        + "}"
    )

    for i in theScript["channels"]["service"]["countries"]:
        name = i["value"]
        link = str("/" + i["code"] + "/en/")
        special = False
        yield {"name": name, "link": link, "special": special}


def fetch_token():
    url = "https://toniandguy.com/"
    global headerz
    with SgChrome() as driver:
        driver.get(url)
        byname_xpath = '/html/body/div/nav/div/div[1]/div[1]/a[2]' #Might break
        byname = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, byname_xpath))
        )
        byname.click()
        time.sleep(5)
        token = driver.page_source.split('"_token" content="',1)[1].split('"',1)[0]
        reqs = list(driver.requests)
        for r in reqs:
            if "salon" in r.path:
                headerz = r.headers
                return token
    return None



def determine_country(country):
    Searchable = country_names_by_code()
    resultName = process.extract(country.name, list(Searchable.values()), limit=1)
    resultCode = process.extract(
        country.link.split("/")[1], list(Searchable.keys()), limit=1
    )
    logzilla.info(
        f"Matched {country.name}{country.link} to {resultName[0]} or {resultCode[0]}"
    )
    if resultName[-1][-1] > resultCode[-1][-1]:
        for i in Searchable.items():
            if i[1] == resultName[-1][0]:
                return i[0]
    else:
        return resultCode[-1][0]



def get_country(search, country, session, headers, SearchableCountry, state):
    def getPoint(point, session, locale, headers):
        if locale[-1] != "/":
            locale = locale + "/"
        url = "https://locate.apple.com{locale}sales/?pt=all&lat={lat}&lon={lon}&address=".format(
            locale=locale, lat=point[0], lon=point[1]
        )
        result = session.get(url, headers=headers)
        soup = b4(result.text, "lxml")
        allscripts = soup.find_all("script")
        thescript = None
        for i in allscripts:
            if "window.resourceLocator.storeSetup" in i.text:
                thescript = i
        if thescript:
            thescript = thescript.text
            thescript = (
                thescript.split("window.resourceLocator.storeSetup = ", 1)[1]
                .rsplit("if(", 1)[0]
                .rsplit(";", 1)[0]
            )
        try:
            locs = json.loads(thescript)
            return locs["results"]
        except Exception as e:
            try:
                logzilla.error(
                    str(
                        f"had some issues with this country and point  {country}\n{point}{url} \n Matched to: {SearchableCountry}\nIssue was\n{str(e)}"
                    )
                )
            except Exception:
                pass

    maxZ = None
    maxZ = search.items_remaining()
    total = 0
    Point = (40.773103, -73.964488)
    try:
        for record in getPoint(Point, session, country.link, headers):
            record["COUNTRY"] = country
            yield record
    except Exception:
        pass
    for Point in search:
        found = 0
        try:
            for record in getPoint(Point, session, country.link, headers):
                search.found_location_at(
                    record["locationData"]["geo"][0], record["locationData"]["geo"][1]
                )
                record["COUNTRY"] = country
                found += 1
                yield record
        except Exception as e:
            try:
                msg = getPoint(Point, session, country.link, headers)
            except Exception as y:
                msg = y
            try:
                logzilla.error(f"Something happened with {msg} \n error is: {e}")
            except Exception as p:
                logzilla.error(f"SMH couldn't even print the error:{e} \n {p}")

        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logzilla.info(
            f"{str(Point).replace('(','').replace(')','')}|found: {found}|total: {total}|prog: {progress}|\nRemaining: {search.items_remaining()} Searchable: {SearchableCountry}"
        )
    if total == 0:
        errorLink = f"https://locate.apple.com{country.link}\n{country.name}"
        logzilla.error(
            f"Found a total of 0 results for country {country}\n this is unacceptable and possibly a country/search space mismatch\n Matched to: {SearchableCountry}\n{errorLink}"
        )



def test_country(country,session):
    #Finds out if we need to search this country.
    headers = {}
    headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    try:
        SgRequests.raise_on_err(session.get())
    except Exception:
        pass
    
def get_Start():
    this = CountryStack(
        seed=OrderedSet(map(lambda r: SerializableCountry.deserialize(r), [])),
        state=None,
    )
    Searchable = country_names_by_code().items()
    for country in Searchable:
        this.push_country(
                SerializableCountry(
                    name=country[1],
                    code=country[0],
                    empty=None,
                    tested=False,
                    retries = 0,
                )
            )
    return this
    
def fetch_data():
    with SgRequests() as session:
        countries = None
        searchables = state.get_misc_value(key="SearchableCountries", value=None)
        try:
            countries = CountryStack(
                seed=OrderedSet(
                    map(
                        lambda r: SerializableCountry.deserialize(r),
                        state.get_misc_value("countries") or [],
                    )
                ),
                state=state,
            )
        except Exception as e:
            logzilla.warning("Something happened along the lines of", exc_info=e)
        if not countries:
            countries = get_Start()
            state.set_misc_value(key="countries", value=countries.serialize_country())
            
            headers = fetch_token()
            headers = headerz
            state.save(override=True)
        country = countries.pop_country()
        while country:
            if not country.tested:
                test_country(country,session)
            if country.empty:
                pass
            else:
                SearchableCountry = state.get_misc_value("SearchableCountry")
                if country.retries < 3:
                    country.retries = country.retries + 1
                    if not SearchableCountry:
                        SearchableCountry = determine_country(country)
                        state.set_misc_value("SearchableCountry", SearchableCountry)
                        state.save(override=True)
                    else:
                        countries.push_country(country)
                        state.set_misc_value(
                            key="countries", value=countries.serialize_country()
                        )
                        state.save(override=True)
                    search = False
                    try:
                        search = DynamicGeoSearch(
                            country_codes=[SearchableCountry],
                            expected_search_radius_miles=None,  # Must turn it back down to 50 after testing
                            max_search_results=100,
                            granularity=Grain_4(),
                        )
                    except Exception as e:
                        errorLink = (
                            f"https://locate.apple.com{country.link}\n{country.name}"
                        )
                        logzilla.warning(
                            f"Issue with sgzip and country code: {SearchableCountry}\n{e}\n{errorLink}"
                        )
                    if SearchableCountry == "hk":
                        search = HKData()
                    if search:
                        for record in get_country(
                            search, country, session, headers, SearchableCountry, state
                        ):
                            yield record
                        SearchableCountry = None
                        state.set_misc_value(
                            key="SearchableCountry", value=SearchableCountry
                        )
                        state.save(override=True)
                    else:
                        SearchableCountry = None
                        state.set_misc_value(
                            key="SearchableCountry", value=SearchableCountry
                        )
                        state.save(override=True)
            country = countries.pop_country()
    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def scrape():
    url = "locate.apple.com"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["storeURL"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["storeName"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["locationData", "geo", 0],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["locationData", "geo", 1],
            is_required=False,
            part_of_record_identity=True,
        ),
        street_address=sp.MultiMappingField(
            mapping=[
                ["locationData", "streetAddress1"],
                ["locationData", "streetAddress2"],
            ],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["locationData", "city"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["locationData", "state"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["locationData", "postalCode"],
            is_required=False,
        ),
        country_code=sp.MappingField(
            mapping=["locationData", "country"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["phoneNumber"],
            part_of_record_identity=True,
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["storeID"],
            is_required=False,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(
            mapping=["storeURL"],
            is_required=False,
        ),
        raw_address=sp.MultiMappingField(
            mapping=[["locationData", "district"], ["locationData", "regionName"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
            is_required=False,
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=25,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
