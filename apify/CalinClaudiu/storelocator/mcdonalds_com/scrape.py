from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from typing import Any, Dict, Optional
import configparser
from csv import reader
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json
import os

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = (
            os.environ["PROXY_URL"]
            if "PROXY_URL" in os.environ
            else None  # Whole function currently not in use, here for httpx
        )
        proxy_url = url.format(proxy_password)
        proxies = {
            "http://": proxy_url,
        }
        return proxies
    else:
        return None


def readConfig(filename):
    config = configparser.ConfigParser(
        allow_no_value=True,
        delimiters=("="),
        comment_prefixes=("#", ";"),
        inline_comment_prefixes=(";"),
    )
    config.read(filename)
    return config


class DataSource:
    class CsvRecord:
        def __init__(self, filename):
            self._filename = filename
            self._row = None
            self._lastSearch = None
            with open(filename, "r", encoding="utf-8") as csvFile:
                file = reader(csvFile)
                self._items_remaining = sum(1 for row in file) - 1

        def items_remaining(self):
            return self._items_remaining

        def found_location_at(self, lat, lng):
            with open("Found_location_at", mode="a", encoding="utf-8") as file:
                if self._lastSearch != self._row:
                    print(str(self._row + ",search"))
                    file.write(str(self._row + ",search\n"))
                    self._lastSearch = self._row

                file.write(str(str(lat) + "," + str(lng) + ",found\n"))
                print(str(str(lat) + "," + str(lng) + ",found"))

        def __iter__(self):
            with open(self._filename, "r", encoding="utf-8") as csvFile:
                file = reader(csvFile)
                keys = next(file)
                for index, row in enumerate(file):
                    row = zip(keys, row)
                    row = dict(row)
                    self._row = str(row["latitude"]) + "," + str(row["longitude"])
                    self._items_remaining -= 1
                    #
                    yield (row["latitude"], row["longitude"])
                    # need to improve on this in config if I ever need it outside of testing


class CleanRecord:
    def China(badRecord, config):
        cleanRecord = {}
        cleanRecord["locator_domain"] = config.get("Domain")
        cleanRecord["page_url"] = ""
        cleanRecord["location_name"] = badRecord["title"]
        cleanRecord["latitude"] = badRecord["location"]["lat"]
        cleanRecord["longitude"] = badRecord["location"]["lng"]
        cleanRecord["street_address1"] = badRecord["address"]
        cleanRecord["street_address2"] = ""
        cleanRecord["city"] = badRecord["city"]
        cleanRecord["state"] = badRecord["province"]
        cleanRecord["zipcode"] = badRecord["district"]
        cleanRecord["country_code"] = "China"
        cleanRecord["phone"] = badRecord["tel"]
        cleanRecord["store_number"] = badRecord["id"]
        cleanRecord["hours_of_operation"] = ""
        cleanRecord["location_type"] = ""
        cleanRecord["raw_address"] = ""
        return cleanRecord

    def USA(badRecord, config):
        cleanRecord = {}
        cleanRecord["locator_domain"] = config.get("Domain")
        cleanRecord["page_url"] = badRecord["xxx"]
        cleanRecord["location_name"] = badRecord["xxx"]
        cleanRecord["latitude"] = badRecord["xxx"]
        cleanRecord["longitude"] = badRecord["xxx"]
        cleanRecord["street_address1"] = badRecord["xxx"]
        cleanRecord["street_address2"] = badRecord["xxx"]
        cleanRecord["city"] = badRecord["xxx"]
        cleanRecord["state"] = badRecord["xxx"]
        cleanRecord["zipcode"] = badRecord["xxx"]
        cleanRecord["country_code"] = badRecord["xxx"]
        cleanRecord["phone"] = badRecord["xxx"]
        cleanRecord["store_number"] = badRecord["xxx"]
        cleanRecord["hours_of_operation"] = badRecord["xxx"]
        cleanRecord["location_type"] = badRecord["xxx"]
        cleanRecord["raw_address"] = badRecord["xxx"]
        return cleanRecord


class CrawlMethod(CleanRecord):
    def China(self):
        def getPointChina(Point):
            url = (
                self._config.get("PostUrl")
                .format(*json.loads(self._config.get("PostUrlFormat")))
                .format(*Point)
            )
            headers = str(self._config.get("Headers"))
            headers = json.loads(headers)
            data = (
                self._config.get("urlencodedData")
                .format(*json.loads(self._config.get("dataFormat")))
                .format(*Point)
            )
            response = self._session.post(url, headers=headers, data=data)
            return response.json()

        record_cleaner = getattr(CleanRecord, self._config.get("cleanupMethod"))
        identities = set()
        maxZ = self._search.items_remaining()
        total = 0
        for Point in self._search:
            found = 0
            results = getPointChina(Point)
            for data in results[str(self._config.get("pathToResults"))]:
                record = record_cleaner(data, self._config)
                self._search.found_location_at(record["latitude"], record["longitude"])
                if (
                    str(
                        str(record["latitude"])
                        + str(record["longitude"])
                        + str(record["phone"])
                        # + str(record["store_number"])
                        + str(record["street_address1"])
                        + str(record["location_name"])
                    )
                    not in identities
                ):
                    identities.add(
                        str(
                            str(record["latitude"])
                            + str(record["longitude"])
                            + str(record["phone"])
                            # + str(record["store_number"])
                            + str(record["street_address1"])
                            + str(record["location_name"])
                        )
                    )
                    found += 1
                    yield record
            progress = (
                str(round(100 - (self._search.items_remaining() / maxZ * 100), 2)) + "%"
            )
            total += found
            logzilla.info(
                f"{[*Point]} | found: {found} | total: {total} | progress: {progress}"
            )

    def USA():
        pass


class getData(CrawlMethod):
    def __init__(
        self,
        config: Dict[str, Any],
        ogProxy: Optional[
            str
        ] = "http://groups-RESIDENTIAL,country-{ProxyCountryCode}:{proxy_password}@proxy.apify.com:8000/",
    ):
        self._config = config
        self._ogProxy = ogProxy
        self._search = None
        self._session = None
        self._driver = None
        self.__init_state()

    def __init_state(self):
        for action in json.loads(self._config.get("Using")):
            func = getattr(getData, action)
            func(self)

    def EnableSGZIP(self):
        module = __import__(str("sgzip." + self._config.get("sgzip")), fromlist=[None])
        search = getattr(module, self._config.get("sgzipType"))
        granularity = getattr(module, self._config.get("sgzipGranularity"))
        SearchableCountries = __import__("sgzip.dynamic", fromlist=[None])
        SearchableCountries = getattr(SearchableCountries, "SearchableCountries")
        Countries = [
            getattr(SearchableCountries, country)
            for country in json.loads(self._config.get("sgzipSearchableCountries"))
        ]
        self._search = search(
            country_codes=Countries,
            max_radius_miles=self._config.getint("sgzipmax_radius_miles")
            if self._config.getint("sgzipmax_radius_miles")
            else None,
            max_search_results=self._config.getint("sgzipmax_search_results")
            if self._config.getint("sgzipmax_search_results")
            else None,
            granularity=granularity(),
        )

    def EnableSGREQUESTS(self):
        self._session = SgRequests()
        # need to improve on that

    def EnableDATASOURCE(self):
        self._search = getattr(DataSource, self._config.get("DataSource"))(
            self._config.get("SourceFileName")
        )

    def Start(self):
        func = getattr(CrawlMethod, self._config.get("Method"))
        return func(self)


def getTestCountries(session):
    url = "https://corporate.mcdonalds.com/corpmcd/our-company/where-we-operate.html"
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    soup = b4(session.get(url, headers=headers).text, "lxml")
    soup = soup.find_all("div", {"class": ["columncontrol", "parbase"]})
    countries = []
    for div in soup:
        for link in div.find_all("a", {"href": True}):
            if link["href"] != "#top":
                if all(j not in link["href"] for j in [":", "/", "www", "http"]):
                    continue
                countries.append(
                    {
                        "text": link.text
                        if len(link.text) > 0
                        else "Unknown{}".format(link["href"]),
                        "page": link["href"],
                    }
                )
    return countries


def todoCountries(config):
    todo = []
    for section in config.items():
        if config[section[0]].getboolean("Considered"):
            config.set(str(section[0]), "Country", str(section[0]))
            todo.append(config[section[0]])

        if config[section[0]].getboolean("Do Only"):
            todo = []
            config.set(str(section[0]), "Country", str(section[0]))
            todo.append(config[section[0]])
            return todo

    for section in todo:
        yield section


def checkFail(countries, fromConfig):
    to_check = set()
    for section in fromConfig:
        to_check.add(section[0])
    for Country in countries:
        if Country["text"] not in to_check:
            logzilla.error(
                "This country: {}\n is missing from mcconfig.ini\n Please add it like this at the end of mcconfig.ini to ignore:\n\n[{}]\nUrl = {}\n\n".format(
                    Country["text"], Country["text"], Country["page"]
                )
            )
            raise Exception


def fix_proxy(StripProxyCountry):
    proxy = os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else None

    if proxy and StripProxyCountry:
        return str(
            proxy.split("country-")[0]
            + "country-{ProxyCountryCode}:{}@proxy"
            + proxy.split("@proxy")[1]
        )
    elif proxy:
        return proxy
    elif StripProxyCountry:
        return proxy


def fetch_data():
    config = readConfig("mcconfig.ini")
    configuredCountries = todoCountries(config)
    ogProxy = fix_proxy(config["DEFAULT"].getboolean("StripProxyCountry"))
    with SgRequests() as session:
        countries = getTestCountries(session)
        checkFail(countries, config.items())
        # Verifies if there's any new countries McDonalds has launched that this crawl isn't aware of.

    for Country in configuredCountries:
        results = getData(config=Country, ogProxy=ogProxy)
        for record in results.Start():
            yield record

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
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["locator_domain"],
        ),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["location_name"], is_required=False),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MultiMappingField(
            mapping=[["street_address1"], ["street_address2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
            is_required=False,
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zipcode"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"], is_required=False
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
        raw_address=sp.MappingField(mapping=["raw_address"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
