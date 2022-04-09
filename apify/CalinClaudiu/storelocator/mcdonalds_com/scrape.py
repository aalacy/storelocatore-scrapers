from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from typing import Any, Dict, Optional
import configparser
import asyncio
from csv import reader
from sgrequests import SgRequests
import httpx
from bs4 import BeautifulSoup as b4
from sgzip.utils import earth_distance
import json
import os
from sgpostal.sgpostal import parse_address_intl

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
os.environ["HTTPX_LOG_LEVEL"] = "trace"


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


proxies = set_proxies()


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
    class GenericRawOutput:
        def __init__(self, config):
            self._config = config
            self._filename = config.get("Country")

        def write(self, string):
            with open(self._filename, mode="a", encoding="utf-8") as file:
                file.write(string)
                file.write("\n")

    class ErrorRetry:
        def __init__(self, errors):
            self._errors = errors
            self._items_remaining = len(self._errors)

        def items_remaining(self):
            return self._items_remaining

        def found_location_at(self, lat, lng):
            pass

        def max_observed_distance(self):
            pass

        def __iter__(self):
            for error in self._errors:
                self._items_remaining -= 1
                yield error["Point"]

    class CsvRecord:
        def __init__(self, filename):
            self._filename = filename
            self._row = None
            self._lastSearch = None
            self.__max_distance_observed = -1
            self.__cur_centroid = None
            with open(filename, "r", encoding="utf-8") as csvFile:
                file = reader(csvFile)
                self._items_remaining = sum(1 for row in file) - 1

        def max_observed_distance(self):
            return self.__max_distance_observed

        def items_remaining(self):
            return self._items_remaining

        def found_location_at(self, lat, lng):
            with open("Found_location_at", mode="a", encoding="utf-8") as file:
                if self._lastSearch != self._row:
                    file.write(str(self._row + ",search\n"))
                    self._lastSearch = self._row
                file.write(str(str(lat) + "," + str(lng) + ",found\n"))
            cur_dist = earth_distance((float(lat), float(lng)), self.__cur_centroid)
            self.__max_distance_observed = max(self.__max_distance_observed, cur_dist)

        def __iter__(self):
            with open(self._filename, "r", encoding="utf-8") as csvFile:
                file = reader(csvFile)
                keys = next(file)
                for index, row in enumerate(file):
                    try:
                        row = zip(keys, row)
                        row = dict(row)
                        self._row = str(row["latitude"]) + "," + str(row["longitude"])
                        self._items_remaining -= 1
                        #
                        self.__cur_centroid = (
                            float(row["latitude"]),
                            float(row["longitude"]),
                        )
                        yield (row["latitude"], row["longitude"])
                    except Exception:
                        continue
                    # need to improve on this in config if I ever need it outside of testing


def drill_down_into(data, path):
    path = json.loads(path)
    for i in path:
        data = data[i]
    return data


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
        cleanRecord["street_address3"] = ""
        cleanRecord["street_address4"] = ""
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

    def USA(badRecord, config, country, locale):
        cleanRecord = {}
        cleanRecord["locator_domain"] = config.get("Domain")
        try:
            cleanRecord["location_name"] = badRecord["properties"]["name"]
        except Exception:
            cleanRecord["location_name"] = None
        cleanRecord["latitude"] = badRecord["geometry"]["coordinates"][1]
        cleanRecord["longitude"] = badRecord["geometry"]["coordinates"][0]
        cleanRecord["street_address1"] = badRecord["properties"]["addressLine1"]
        if not cleanRecord["location_name"]:
            try:
                cleanRecord["location_name"] = badRecord["properties"]["addressLine2"]
            except Exception:
                cleanRecord["street_address2"] = ""
        else:
            try:
                badRecord["properties"]["addressLine2"] = badRecord["properties"][
                    "addressLine2"
                ]
                cleanRecord["street_address2"] = badRecord["properties"]["addressLine2"]
            except Exception:
                cleanRecord["street_address2"] = ""
        cleanRecord["street_address3"] = ""
        cleanRecord["street_address4"] = ""
        try:
            cleanRecord["city"] = badRecord["properties"]["addressLine3"]
        except Exception:
            cleanRecord["city"] = ""
        try:
            cleanRecord["state"] = badRecord["properties"]["subDivision"]
        except Exception:
            cleanRecord["state"] = ""
        try:
            cleanRecord["zipcode"] = badRecord["properties"]["postcode"]
        except Exception:
            cleanRecord["zipcode"] = ""
        try:
            cleanRecord["country_code"] = badRecord["properties"]["addressLine4"]
        except Exception:
            cleanRecord["country_code"] = ""
        try:
            cleanRecord["phone"] = badRecord["properties"]["telephone"]
        except Exception:
            cleanRecord["phone"] = ""
        cleanRecord["store_number"] = badRecord["properties"]["id"]
        try:
            cleanRecord["hours_of_operation"] = (
                str(list(badRecord["properties"]["restauranthours"].items()))
                .replace("'", "")
                .replace("(", "")
                .replace(")", "")
                .replace("[", "")
                .replace("]", "")
                .replace("hours", "")
            )
        except Exception:
            cleanRecord["hours_of_operation"] = ""
        cleanRecord["location_type"] = (
            badRecord["properties"]["filterType"]
            if "OPEN" in badRecord["properties"]["openstatus"]
            else badRecord["properties"]["openstatus"]
        )
        cleanRecord["raw_address"] = ""
        identifier = None

        for dent in badRecord["properties"]["identifiers"]["storeIdentifier"]:
            if dent["identifierType"] == "NSN":
                identifier = dent["identifierValue"]
        if identifier:
            cleanRecord["page_url"] = "https://{}/{}/{}/location/{}.html".format(
                cleanRecord["locator_domain"], country, locale, identifier
            )
        else:
            try:
                cleanRecord["page_url"] = "https://{}/{}/{}/location/{}.html".format(
                    cleanRecord["locator_domain"],
                    country,
                    locale,
                    badRecord["properties"]["identifiers"]["storeIdentifier"][1][
                        "identifierValue"
                    ],
                )
            except Exception:
                cleanRecord["page_url"] = "https://{}/{}/{}/location/{}.html".format(
                    cleanRecord["locator_domain"],
                    country,
                    locale,
                    badRecord["properties"]["identifiers"]["storeIdentifier"][0][
                        "identifierValue"
                    ],
                )

        return cleanRecord

    def USA2(badRecord, config, country, locale):
        cleanRecord = {}
        cleanRecord["locator_domain"] = config.get("Domain")
        try:
            cleanRecord["location_name"] = badRecord["properties"]["name"]
        except Exception:
            cleanRecord["location_name"] = None
        cleanRecord["latitude"] = badRecord["geometry"]["coordinates"][1]
        cleanRecord["longitude"] = badRecord["geometry"]["coordinates"][0]
        cleanRecord["street_address1"] = badRecord["properties"]["addressLine1"]
        if not cleanRecord["location_name"]:
            try:
                cleanRecord["location_name"] = badRecord["properties"]["addressLine2"]
            except Exception:
                cleanRecord["street_address2"] = ""
        else:
            try:
                badRecord["properties"]["addressLine2"] = badRecord["properties"][
                    "addressLine2"
                ]
                cleanRecord["street_address2"] = badRecord["properties"]["addressLine2"]
            except Exception:
                cleanRecord["street_address2"] = ""
        cleanRecord["street_address3"] = ""
        cleanRecord["street_address4"] = ""
        try:
            cleanRecord["city"] = badRecord["properties"]["addressLine3"]
        except Exception:
            cleanRecord["city"] = ""
        try:
            cleanRecord["state"] = badRecord["properties"]["subDivision"]
        except Exception:
            cleanRecord["state"] = ""
        try:
            cleanRecord["zipcode"] = badRecord["properties"]["postcode"]
        except Exception:
            cleanRecord["zipcode"] = ""
        try:
            cleanRecord["country_code"] = badRecord["properties"]["addressLine4"]
        except Exception:
            cleanRecord["country_code"] = ""
        try:
            cleanRecord["phone"] = badRecord["properties"]["telephone"]
        except Exception:
            cleanRecord["phone"] = ""
        cleanRecord["store_number"] = badRecord["properties"]["id"]
        try:
            cleanRecord["hours_of_operation"] = (
                str(list(badRecord["properties"]["restauranthours"].items()))
                .replace("'", "")
                .replace("(", "")
                .replace(")", "")
                .replace("[", "")
                .replace("]", "")
                .replace("hours", "")
            )
        except Exception:
            cleanRecord["hours_of_operation"] = ""
        cleanRecord["location_type"] = (
            badRecord["properties"]["filterType"]
            if "OPEN" in badRecord["properties"]["openstatus"]
            else badRecord["properties"]["openstatus"]
        )
        cleanRecord["raw_address"] = ""
        identifier = None
        cleanRecord["page_url"] = None
        try:
            cleanRecord["page_url"] = "https://{}/{}/{}/location/{}.html".format(
                cleanRecord["locator_domain"],
                country,
                locale,
                badRecord["properties"]["identifierValue"],
            )
            cleanRecord["store_number"] = badRecord["properties"]["identifierValue"]
        except Exception:
            cleanRecord["page_url"] = None

        if not cleanRecord["page_url"]:
            for dent in badRecord["properties"]["identifiers"]["storeIdentifier"]:
                if dent["identifierType"] == "NSN":
                    identifier = dent["identifierValue"]
            if identifier:
                cleanRecord["page_url"] = "https://{}/{}/{}/location/{}.html".format(
                    cleanRecord["locator_domain"], country, locale, identifier
                )
            else:
                try:
                    cleanRecord[
                        "page_url"
                    ] = "https://{}/{}/{}/location/{}.html".format(
                        cleanRecord["locator_domain"],
                        country,
                        locale,
                        badRecord["properties"]["identifiers"]["storeIdentifier"][1][
                            "identifierValue"
                        ],
                    )
                except Exception:
                    cleanRecord[
                        "page_url"
                    ] = "https://{}/{}/{}/location/{}.html".format(
                        cleanRecord["locator_domain"],
                        country,
                        locale,
                        badRecord["properties"]["identifiers"]["storeIdentifier"][0][
                            "identifierValue"
                        ],
                    )

        return cleanRecord

    def DEDUPE(badRecord):
        cleanRecord = {}
        cleanRecord["locator_domain"] = badRecord["locator_domain"]
        cleanRecord["page_url"] = badRecord["page_url"]
        cleanRecord["location_name"] = badRecord["location_name"]
        cleanRecord["latitude"] = badRecord["latitude"]
        cleanRecord["longitude"] = badRecord["longitude"]
        cleanRecord["street_address1"] = badRecord["street_address"]
        cleanRecord["street_address2"] = ""
        cleanRecord["street_address3"] = ""
        cleanRecord["street_address4"] = ""
        cleanRecord["city"] = badRecord["city"]
        cleanRecord["state"] = badRecord["state"]
        cleanRecord["zipcode"] = badRecord["zip"]
        cleanRecord["country_code"] = badRecord["country_code"]
        cleanRecord["phone"] = badRecord["phone"]
        cleanRecord["store_number"] = badRecord["store_number"]
        cleanRecord["hours_of_operation"] = badRecord["hours_of_operation"]
        cleanRecord["location_type"] = badRecord["location_type"]
        cleanRecord["raw_address"] = badRecord["raw_address"]
        return cleanRecord

    def Ecuador(badRecord, config):
        copy = badRecord["name"]
        if "<" and ">" in copy:
            copy = copy.replace("<", "<?<")
            copy = copy.split("<?")
            newdata = []
            for string in copy:
                topop = []
                i = 0
                while i < len(string):
                    if string[i] == "<":
                        topop.append(i)
                        i += 1
                        while string[i] != ">" and i < len(string):
                            topop.append(i)
                            i += 1
                        topop.append(i)
                    i += 1
                string = list(string)
                for i in reversed(topop):
                    string.pop(i)
                string = "".join(string)
                if len(string) > 0:
                    newdata.append(string.strip())
            cleanRecord = {}
            cleanRecord["locator_domain"] = config.get("Domain")
            cleanRecord["page_url"] = ""
            cleanRecord["location_name"] = newdata[0]
            cleanRecord["latitude"] = badRecord["latitude"]
            cleanRecord["longitude"] = badRecord["longitude"]
            cleanRecord["street_address1"] = newdata[1]
            cleanRecord["street_address2"] = ""
            cleanRecord["street_address3"] = ""
            cleanRecord["street_address4"] = ""
            cleanRecord["city"] = ""
            cleanRecord["state"] = ""
            cleanRecord["zipcode"] = ""
            cleanRecord["country_code"] = ""
            cleanRecord["phone"] = ""
            cleanRecord["store_number"] = badRecord["id"]
            cleanRecord["hours_of_operation"] = ""
            cleanRecord["location_type"] = badRecord["services"]
            cleanRecord["raw_address"] = ""
        else:
            newdata = copy
            parsed = parse_address_intl(
                newdata.replace(",", " ").replace("\r", "").replace("\n", "")
            )
            cleanRecord = {}
            cleanRecord["locator_domain"] = config.get("Domain")
            cleanRecord["page_url"] = ""
            cleanRecord["location_name"] = ""
            cleanRecord["latitude"] = badRecord["latitude"]
            cleanRecord["longitude"] = badRecord["longitude"]
            cleanRecord["street_address1"] = parsed.street_address_1
            cleanRecord["street_address2"] = parsed.street_address_2
            cleanRecord["street_address3"] = ""
            cleanRecord["street_address4"] = ""
            cleanRecord["city"] = parsed.city
            cleanRecord["state"] = parsed.state
            cleanRecord["zipcode"] = parsed.postcode
            cleanRecord["zipcode"] = cleanRecord["zipcode"].replace("None", "<MISSING>")
            cleanRecord["country_code"] = parsed.country
            cleanRecord["country_code"] = cleanRecord["country_code"].replace(
                "None", "<MISSING>"
            )
            cleanRecord["phone"] = ""
            cleanRecord["store_number"] = badRecord["id"]
            cleanRecord["hours_of_operation"] = ""
            cleanRecord["location_type"] = badRecord["services"]
            cleanRecord["raw_address"] = newdata
        return cleanRecord

    def EcuadorEspecial(badRecord, config):
        copy = badRecord["name"]
        if "<" and ">" in copy:
            copy = copy.replace("<", "<?<")
            copy = copy.split("<?")
            newdata = []
            for string in copy:
                topop = []
                i = 0
                while i < len(string):
                    if string[i] == "<":
                        topop.append(i)
                        i += 1
                        while string[i] != ">" and i < len(string):
                            topop.append(i)
                            i += 1
                        topop.append(i)
                    i += 1
                string = list(string)
                for i in reversed(topop):
                    string.pop(i)
                string = "".join(string)
                if len(string) > 0:
                    newdata.append(string.strip())
            cleanRecord = {}
            cleanRecord["locator_domain"] = config.get("Domain")
            cleanRecord["page_url"] = ""
            cleanRecord["location_name"] = newdata[0]
            cleanRecord["latitude"] = badRecord["latitude"]
            cleanRecord["longitude"] = badRecord["longitude"]
            cleanRecord["street_address1"] = newdata[1]
            cleanRecord["street_address2"] = ""
            cleanRecord["street_address3"] = ""
            cleanRecord["street_address4"] = ""
            cleanRecord["city"] = ""
            cleanRecord["state"] = ""
            cleanRecord["zipcode"] = ""
            cleanRecord["country_code"] = ""
            cleanRecord["phone"] = ""
            cleanRecord["store_number"] = badRecord["id"]
            cleanRecord["hours_of_operation"] = cleanRecord["street_address1"]
            cleanRecord["street_address1"] = ""
            cleanRecord["location_type"] = badRecord["services"]
            cleanRecord["raw_address"] = ""
        else:
            newdata = copy
            parsed = parse_address_intl(
                newdata.replace(",", " ").replace("\r", "").replace("\n", "")
            )
            cleanRecord = {}
            cleanRecord["locator_domain"] = config.get("Domain")
            cleanRecord["page_url"] = ""
            cleanRecord["location_name"] = ""
            cleanRecord["latitude"] = badRecord["latitude"]
            cleanRecord["longitude"] = badRecord["longitude"]
            cleanRecord["street_address1"] = parsed.street_address_1
            cleanRecord["street_address2"] = parsed.street_address_2
            cleanRecord["street_address3"] = ""
            cleanRecord["street_address4"] = ""
            cleanRecord["city"] = parsed.city
            cleanRecord["state"] = parsed.state
            cleanRecord["zipcode"] = parsed.postcode
            cleanRecord["zipcode"] = cleanRecord["zipcode"].replace("None", "<MISSING>")
            cleanRecord["country_code"] = parsed.country
            cleanRecord["country_code"] = cleanRecord["country_code"].replace(
                "None", "<MISSING>"
            )
            cleanRecord["phone"] = ""
            cleanRecord["store_number"] = badRecord["id"]
            cleanRecord["hours_of_operation"] = cleanRecord["street_address1"]
            cleanRecord["street_address1"] = ""
            cleanRecord["location_type"] = badRecord["services"]
            cleanRecord["raw_address"] = newdata
        return cleanRecord

    def __PLACEHOLDER(badRecord, config):
        cleanRecord = {}
        cleanRecord["locator_domain"] = config.get("Domain")
        cleanRecord["page_url"] = badRecord["xxx"]
        cleanRecord["location_name"] = badRecord["xxx"]
        cleanRecord["latitude"] = badRecord["xxx"]
        cleanRecord["longitude"] = badRecord["xxx"]
        cleanRecord["street_address1"] = badRecord["xxx"]
        cleanRecord["street_address2"] = ""
        cleanRecord["street_address3"] = ""
        cleanRecord["street_address4"] = ""
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
    def OneLink(self):
        def getPage():
            url = self._config.get("GetUrl")
            headers = str(self._config.get("Headers"))
            headers = json.loads(headers)
            response = self._session.post(url, headers=headers)
            return response.json()

        record_cleaner = getattr(CleanRecord, self._config.get("cleanupMethod"))
        data = getPage()
        if data:
            try:
                for records in drill_down_into(
                    data, str(self._config.get("pathToResults"))
                ):
                    record = record_cleaner(records, self._config)
                    yield record
            except Exception as e:
                logzilla.info(f"Had issues, issue:\n{str(e)}")

    def AsyncChina(self):
        async def getPointChina(Point):
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
            async with httpx.AsyncClient(
                proxies=proxies, headers=headers, timeout=None
            ) as client:
                try:
                    data = {}
                    response = await client.post(url, headers=headers, data=data)
                    response = response.json()
                    data["response"] = response
                    data["SEARCHPOINT"] = Point
                    return data
                except Exception as e:
                    self.Oopsie(Point, str(e))

        record_cleaner = getattr(CleanRecord, self._config.get("cleanupMethod"))
        maxZ = self._search.items_remaining()
        total = 0
        chunk_size = self._config.getint("Concurrency")  # type: ignore
        task_list = []
        points_list = []

        async def search(task_list):
            z = await asyncio.gather(*task_list)
            return z

        for Point in self._search:
            data = None
            if len(task_list) == chunk_size:
                data = asyncio.run(search(task_list))
                task_list = []
                task_list.append(getPointChina(Point))
            else:
                task_list.append(getPointChina(Point))
                points_list.append(Point)
                continue
            if data:
                found = 0
                for results in data:
                    try:
                        for records in results["response"][
                            str(self._config.get("pathToResults"))
                        ]:
                            record = record_cleaner(records, self._config)
                            self._search.found_location_at(
                                record["latitude"], record["longitude"]
                            )
                            found += 1
                            yield record
                    except Exception as e:
                        try:
                            self.Oopsie(results["SEARCHPOINT"], str(e))
                        except Exception:
                            pass

            remaining = self._search.items_remaining()
            if remaining == 0:
                remaining = 1
            if maxZ < remaining:
                maxZ = remaining
            found = 0
            progress = str(round(100 - (remaining / maxZ * 100), 2)) + "%"
            total += found
            logzilla.info(
                f"{[*points_list]}\n | found: {found} | total: {total} | progress: {progress} | Concurrency: {chunk_size}\n"
            )
            points_list = []
            points_list.append(Point)
        if len(task_list) != 0:
            data = asyncio.run(search(task_list))
            for results in data:
                for records in results[str(self._config.get("pathToResults"))]:
                    record = record_cleaner(records, self._config)
                    yield record
            logzilla.info(
                f"{[*points_list]}\n | found: {found} | total: {total} | progress: {progress} | Concurrency: {len(task_list)}\n"
            )

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
        # identities = set() # noqa
        maxZ = self._search.items_remaining()
        total = 0
        for Point in self._search:
            remaining = self._search.items_remaining()
            if remaining == 0:
                remaining = 1
            if maxZ < remaining:
                maxZ = remaining
            found = 0
            try:
                results = getPointChina(Point)
            except Exception as e:
                self.Oopsie(Point, str(e))
                continue
            try:
                for data in results[str(self._config.get("pathToResults"))]:
                    record = record_cleaner(data, self._config)
                    self._search.found_location_at(
                        record["latitude"], record["longitude"]
                    )
                    # if ( # noqa
                    #    str(
                    #        str(record["latitude"]) # noqa
                    #        + str(record["longitude"]) # noqa
                    #        + str(record["phone"]) # noqa
                    #        #+ str(record["store_number"]) # noqa
                    #        + str(record["street_address1"]) # noqa
                    #        + str(record["location_name"]) # noqa
                    #    ) # noqa
                    #    not in identities # noqa
                    # ): # noqa
                    #    identities.add( # noqa
                    #       str( # noqa
                    #            str(record["latitude"]) # noqa
                    #           + str(record["longitude"]) # noqa
                    #           + str(record["phone"]) # noqa
                    #            #+ str(record["store_number"]) # noqa
                    #           + str(record["street_address1"]) # noqa
                    #           + str(record["location_name"]) # noqa
                    #        ) # noqa
                    #    ) # noqa
                    found += 1
                    yield record
            except Exception as e:
                self.Oopsie(Point, str(e))
                continue
            progress = str(round(100 - (remaining / maxZ * 100), 2)) + "%"
            total += found
            logzilla.info(
                f"{[*Point]} | found: {found} | total: {total} | progress: {progress}"
            )

    def USA(self):
        def getAllData(headers, country, locale):
            if self._config.get("apiCountry"):
                country = self._config.get("apiCountry")
            api = "https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=0&longitude=0&radius=100000&maxResults=25000&country={}&language={}"
            api = api.format(country, locale)
            return self._session.get(api, headers=headers).json()

        def getLocale(headers):
            link = headers["referer"]
            return link.split("/")[3:5]

        def getReferer(url):
            soup = b4(self._session.get(url).text, "lxml")
            link = url.split("/")[:3]
            link = "/".join(link)
            link = (
                link
                + soup.find("a", {"href": lambda x: x and "restaurant-locator" in x})[
                    "href"
                ]
            )
            return link

        record_cleaner = getattr(CleanRecord, self._config.get("cleanupMethod"))
        headers = {}
        headers["referer"] = getReferer(self._config.get("Url"))
        country, locale = getLocale(headers)
        results = getAllData(headers, country, locale)
        if self._Logger:
            self._Logger.write(json.dumps(results))
        for data in results[str(self._config.get("pathToResults"))]:
            record = record_cleaner(data, self._config, country, locale)
            yield record

    def USA2(self):
        def getAllData(headers, country, locale, Point):
            if self._config.get("apiCountry"):
                country = self._config.get("apiCountry")
            api = "https://www.mcdonalds.com/googleappsv2/geolocation?latitude={}&longitude={}&radius=1000&maxResults=25000&country={}&language={}"
            api = api.format(Point[0], Point[1], country, locale)
            return self._session.get(api, headers=headers).json()

        def getLocale(headers):
            link = headers["referer"]
            return link.split("/")[3:5]

        def getReferer(url):
            soup = b4(self._session.get(url).text, "lxml")
            link = url.split("/")[:3]
            link = "/".join(link)
            link = (
                link
                + soup.find("a", {"href": lambda x: x and "restaurant-locator" in x})[
                    "href"
                ]
            )
            return link

        record_cleaner = getattr(CleanRecord, self._config.get("cleanupMethod"))
        maxZ = self._search.items_remaining()
        for Point in self._search:
            remaining = self._search.items_remaining()
            if remaining == 0:
                remaining = 1
            if maxZ < remaining:
                maxZ = remaining
            found = 0
            try:
                headers = {}
                headers["referer"] = getReferer(self._config.get("Url"))
                country, locale = getLocale(headers)
                headers = {}
                results = results = getAllData(headers, country, locale, Point)
            except Exception as e:
                self.Oopsie(Point, str(e))
                continue
            try:
                for data in results[str(self._config.get("pathToResults"))]:
                    record = record_cleaner(data, self._config, country, locale)
                    self._search.found_location_at(
                        record["latitude"], record["longitude"]
                    )
                    found += 1
                    yield record
            except Exception as e:
                self.Oopsie(Point, str(e))
                continue

    def QuickDedupe(self):
        record_cleaner = CleanRecord.DEDUPE
        files = str(self._config.get("DedupeFiles"))
        files = json.loads(files)
        for file in files:
            with open(file, mode="r", encoding="utf-8") as doc:
                csvFile = reader(doc)
                keys = next(csvFile)
                for index, row in enumerate(csvFile):
                    row = zip(keys, row)
                    row = dict(row)
                    record = record_cleaner(row)
                    yield record


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
        self._errors = None
        self._Logger = None
        self._errorRetries = self._config.getint("Error Retries")  # type: ignore
        self.__init_state()

    def __init_state(self):
        for action in json.loads(self._config.get("Using")):
            func = getattr(getData, action)
            func(self)

    def Close(self):
        for action in json.loads(self._config.get("Using")):
            try:
                func = getattr(getData, str(str(action) + "close"))
                func(self)
            except AttributeError:
                pass

    def EnableMaintenanceRecord(self):
        self._Logger = getattr(DataSource, self._config.get("MaintenanceLogger"))(
            self._config
        )

    def EnableSGSELENIUM(self):
        pass

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
            expected_search_radius_miles=self._config.getint("sgzipmax_radius_miles")  # type: ignore
            if self._config.getint("sgzipmax_radius_miles")  # type: ignore
            else None,
            max_search_results=self._config.getint("sgzipmax_search_results")  # type: ignore
            if self._config.getint("sgzipmax_search_results")  # type: ignore
            else None,
            granularity=granularity(),
        )

    def EnableSGREQUESTS(self):
        self._session = SgRequests()

    def EnableSGREQUESTSclose(self):
        self._session.close()

    def EnableDATASOURCE(self):
        self._search = getattr(DataSource, self._config.get("DataSource"))(
            self._config.get("SourceFileName")
        )

    def Oopsie(self, Point, exception):
        if not self._errors:
            self._errors = []
        with open("errors.csv", mode="a", encoding="utf-8") as file:
            file.write(
                str(
                    str(Point[0])
                    + ","
                    + str(Point[1])
                    + ",error,"
                    + str(exception)
                    + "\n"
                )
            )
            self._errors.append({"Point": Point, "error": str(exception)})

    def Start(self):
        func = getattr(CrawlMethod, self._config.get("Method"))
        return func(self)

    def Done(self):
        if self._errors:
            try:
                func = getattr(CrawlMethod, self._config.get("ErrorMethod"))
                self._search = DataSource.ErrorRetry(self._errors)
                attempted = 0
                while attempted < self._errorRetries:
                    attempted += 1
                    yield func(self)
            except Exception:
                pass
        getData.Close(self)


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
        if config[section[0]].getboolean("Do OOOOOOOOnly"):
            todo = []
            config.set(str(section[0]), "Country", str(section[0]))
            todo.append(config[section[0]])
            break

    for section in todo:
        yield section


def notdoneCountries(config):
    todo = []
    for section in config.items():
        if not config[section[0]].getboolean("Considered"):
            config.set(str(section[0]), "Country", str(section[0]))
            todo.append(config[section[0]])
        if config[section[0]].getboolean("Do OOOOOOOOnly"):
            todo = []
            config.set(str(section[0]), "Country", str(section[0]))
            todo.append(config[section[0]])
            break

    for section in todo:
        yield section


def checkFail(countries, fromConfig):
    to_check = set()
    for section in fromConfig:
        to_check.add(section[0])
    for Country in countries:
        if any(
            i in Country["text"]
            for i in [
                "Русский",
                "қазақ",
                "Detsch",
                "عربي",
                "Italiano",
                "Русский",
                "беларуская",
                "ქართული",
                "Ελληνικά",
                "Français",
                "Español",
                "Azərbaycan",
            ]
        ):
            continue
        if Country["text"] not in to_check:
            logzilla.error(
                "\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nThis country: {}\n is missing from mcconfig.ini\n Please add it like this at the end of mcconfig.ini to ignore:\n\n[{}]\nUrl = {}\n\n".format(
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
    logzilla.info(f"Crawler pulled these countries:")  # noqa
    configuredCountrie = todoCountries(config)
    for Country in configuredCountrie:
        logzilla.info(f"{Country}")  # noqa

    logzilla.info(f"Crawler did not pull these countries:")  # noqa
    configuredCountrie = notdoneCountries(config)
    for Country in configuredCountrie:
        logzilla.info(f"{Country}")  # noqa
    with SgRequests() as session:
        countries = getTestCountries(session)
        checkFail(countries, config.items())
        # Verifies if there's any new countries McDonalds has launched that this crawl isn't aware of.

    for Country in configuredCountries:
        logzilla.info(f"Starting : {Country}")
        results = getData(config=Country, ogProxy=ogProxy)
        for record in results.Start():
            yield record
        newrec = 0
        for attempt in results.Done():
            logzilla.info("Tried to fix errors")  # noqa
            for record in attempt:
                newrec += 1
                yield record
        logzilla.info(f"New records found (when fixing errors) : {newrec}")  # noqa
        logzilla.info(f"Finished : {Country}")

    logzilla.info(f"Crawler pulled these countries:")  # noqa
    configuredCountries = todoCountries(config)
    for Country in configuredCountries:
        logzilla.info(f"{Country}")  # noqa

    logzilla.info(f"Crawler did not pull these countries:")  # noqa
    configuredCountries = notdoneCountries(config)
    for Country in configuredCountries:
        logzilla.info(f"{Country}")  # noqa

    logzilla.info(f"Finished grabbing data!!")  # noqa


def strip_parantheses(x):
    result = []
    c = 0
    inside = False
    waitfor = None
    this = {"{": "}", "[": "]", "(": ")"}
    length = len(x)
    while c < length:
        if any(i == x[c] for i in ["{", "[", "("]):
            inside = True
            waitfor = this[x[c]]
        if x[c] != waitfor:
            if not inside:
                result.append(x[c])
        else:
            inside = False
        c += 1

    return "".join(result)


def fix_comma(x):
    h = []
    result = None
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        result = ", ".join(h).replace("  ", " ")
    except Exception:
        result = x.replace("  ", " ")
    return strip_parantheses(result)


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["locator_domain"],
        ),
        page_url=sp.MappingField(
            mapping=["page_url"],
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        location_name=sp.MappingField(
            mapping=["location_name"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        street_address=sp.MultiMappingField(
            mapping=[["street_address1"], ["street_address2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
            is_required=False,
            part_of_record_identity=True,
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zipcode"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(
            mapping=["phone"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["store_number"],
            is_required=False,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"],
            is_required=False,
            value_transform=lambda x: x.replace("\n", " ").replace("\r", " "),
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
        raw_address=sp.MappingField(mapping=["raw_address"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=1000,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
