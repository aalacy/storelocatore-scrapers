from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, Grain_8
from sgzip.utils import country_names_by_code
from fuzzywuzzy import process
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sgscrape.pause_resume import CrawlStateSingleton, CrawlState
from dataclasses import asdict, dataclass
from typing import Iterable, Optional
from ordered_set import OrderedSet
import json


logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
known_empties = set()
known_empties.add("xxxxxxx")

errorz = ["test"]


@dataclass(frozen=False)
class SerializableCountry:
    """
    Consists of fields that define a country.
    """

    name: str
    link: str
    special: bool
    retries: int

    def serialize(self) -> str:
        return json.dumps(asdict(self))

    def __hash__(self):
        return hash((self.name, self.link, self.special))

    def __eq__(self, other):
        return isinstance(other, SerializableCountry) and hash(self) == hash(other)

    @staticmethod
    def deserialize(serialized_json: str) -> "SerializableCountry":
        as_dict = json.loads(serialized_json)
        return SerializableCountry(
            name=as_dict["name"],
            link=as_dict["link"],
            special=as_dict["special"],
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

    def serialize_requests(self) -> Iterable[str]:  # type: ignore
        return list(map(lambda r: r.serialize(), self.__country_stack))  # type: ignore

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.__country_stack)

    def __next__(self):
        req = self.pop_request()
        return req


def get_Start(session, headers):
    page = session.get("https://locate.apple.com/findlocations", headers=headers)
    soup = b4(page.text, "lxml")
    data = []
    soup = soup.find("div", {"class": "content selfclear", "id": "content"}).find_all(
        "li"
    )
    for i in soup:
        name = i.find("span").text
        link = i.find("a")["href"]
        found = False
        for index, country in enumerate(data):
            if link.split("/")[1] == country["link"].split("/")[1]:
                if "/en/" in link:
                    data[index]["link"] = link
                    data[index]["name"] = name
                found = True
        if not found:
            if len(link) > 7:
                data.append({"name": name, "link": link, "special": True})
            else:
                data.append({"name": name, "link": link, "special": False})

    this = CountryStack(
        seed=OrderedSet(map(lambda r: SerializableCountry.deserialize(r), [])),
        state=None,
    )
    for item in data:
        this.push_country(
            SerializableCountry(
                name=item["name"], link=item["link"], special=item["special"], retries=0
            )
        )
    return this


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
    global errorz
    errorzCopy = None
    if errorz:
        if len(errorz) != 0:
            errorzCopy = errorz
        try:
            errorz = state.get_misc_value("errorz")
        except Exception as e:
            logzilla.warning("Something happened along the lines of", exc_info=e)
        if errorz and errorzCopy:
            errorz = errorz + errorzCopy
            state.set_misc_value("errorz", errorz)
            state.save(override=True)
        else:
            if not errorz:
                if errorzCopy:
                    state.set_misc_value("errorz", errorzCopy)
                    state.save(override=True)

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
                errorz.append(
                    str(
                        f"had some issues with this country and point  {country}\n{point}{url} \n Matched to: {SearchableCountry}\nIssue was\n{str(e)}"
                    )
                )
            except Exception:
                pass

    maxZ = None
    maxZ = search.items_remaining()
    total = 0
    for Point in search:
        if total > 50:
            break
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
        logzilla.error(
            f"Found a total of 0 results for country {country}\n this is unacceptable and possibly a country/search space mismatch\n Matched to: {SearchableCountry}"
        )
        if SearchableCountry not in known_empties:
            if errorz:
                errorz.append(
                    str(
                        f"Found a total of 0 results for country {country}\n this is unacceptable and possibly a country/search space mismatch\n Matched to: {SearchableCountry}"
                    )
                )
            errorzCopy = None
            if errorz:
                if len(errorz) != 0:
                    errorzCopy = errorz
            try:
                errorz = state.get_misc_value("errorz")
            except Exception as e:
                logzilla.warning("Something happened along the lines of", exc_info=e)
            if errorz and errorzCopy:
                newErrorz = []
                for i in errorz:
                    if i not in newErrorz:
                        newErrorz.append(i)

                for i in errorzCopy:
                    if i not in newErrorz:
                        newErrorz.append(i)
                state.set_misc_value("errorz", newErrorz)
                state.save(override=True)
            else:
                if not errorz:
                    if errorzCopy:
                        state.set_misc_value("errorz", errorzCopy)
                        state.save(override=True)


state = CrawlStateSingleton.get_instance()


def fetch_data():
    global errorz
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    with SgRequests() as session:
        countries = None
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
            countries = get_Start(session, headers)
            state.set_misc_value(key="countries", value=countries.serialize_requests())
            state.set_misc_value(key="SearchableCountry", value=None)
            state.save(override=True)
        errorzCopy = None
        if errorz:
            if len(errorz) != 0:
                errorzCopy = errorz
        try:
            errorz = state.get_misc_value("errorz")
        except Exception as e:
            logzilla.warning("Something happened along the lines of", exc_info=e)
        if errorz and errorzCopy:
            newErrorz = []
            for i in errorz:
                if i not in newErrorz:
                    newErrorz.append(i)

            for i in errorzCopy:
                if i not in newErrorz:
                    newErrorz.append(i)
            state.set_misc_value("errorz", newErrorz)
            state.save(override=True)
        else:
            if not errorz:
                if errorzCopy:
                    state.set_misc_value("errorz", errorzCopy)
                    state.save(override=True)

        country = countries.pop_country()
        while country:
            if country.special:
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
                            key="countries", value=countries.serialize_requests()
                        )
                        state.save(override=True)
                    search = False
                    try:
                        search = DynamicGeoSearch(
                            country_codes=[SearchableCountry],
                            expected_search_radius_miles=50,
                            max_search_results=None,
                            granularity=Grain_8(),
                        )
                    except Exception as e:
                        logzilla.warning(
                            f"Issue with sgzip and country code: {SearchableCountry}\n{e}"
                        )
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
        ),
        longitude=sp.MappingField(
            mapping=["locationData", "geo", 1],
            is_required=False,
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
            part_of_record_identity=True,
            is_required=False,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MissingField(),
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
    )

    pipeline.run()
    global errorz
    errorzCopy = None
    if errorz:
        if len(errorz) != 0:
            errorzCopy = errorz
    try:
        errorz = state.get_misc_value("errorz")
    except Exception as e:
        logzilla.warning("Something happened along the lines of", exc_info=e)
    if errorz and errorzCopy:
        newErrorz = []
        for i in errorz:
            if i not in newErrorz:
                newErrorz.append(i)

        for i in errorzCopy:
            if i not in newErrorz:
                newErrorz.append(i)
        state.set_misc_value("errorz", newErrorz)
        state.save(override=True)
    else:
        if not errorz:
            if errorzCopy:
                state.set_misc_value("errorz", errorzCopy)
                state.save(override=True)
                errorz = errorzCopy
    for i in errorz:
        logzilla.warning(i)
    raise


if __name__ == "__main__":
    scrape()
