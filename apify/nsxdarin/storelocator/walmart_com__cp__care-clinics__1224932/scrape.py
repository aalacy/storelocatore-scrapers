from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from requests import exceptions  # noqa
from urllib3 import exceptions as urllibException
from bs4 import BeautifulSoup as b4
from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
import json

logger = SgLogSetup().get_logger("walmart_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    expected_search_radius_miles=8,
    max_search_results=50,
)


def api_get(start_url, headers, attempts, maxRetries):
    error = False
    session = SgRequests()
    try:
        results = SgRequests.raise_on_err(session.get(start_url, headers=headers))
    except exceptions.RequestException as requestsException:
        if "ProxyError" in str(requestsException):
            attempts += 1
            error = True
        else:
            raise requestsException

    except urllibException.SSLError as urlException:
        if "BAD_RECORD_MAC" in str(urlException):
            attempts += 1
            error = True
        else:
            raise urllibException

    if error:
        if attempts < maxRetries:
            results = api_get(start_url, headers, attempts, maxRetries)
        else:
            TooManyRetries = (
                "Retried "
                + str(maxRetries)
                + " times, got either SSLError or ProxyError"
            )
            raise TooManyRetries
    else:
        return results


def grab_json(soup):
    son = soup.find_all("script")
    for i in reversed(son):
        if "REDUX" in i.text:
            data = i.text.split("TE__ = ", 1)[1].rsplit(";", 1)[0]
            return json.loads(data)["store"]


def other_source(session, state):
    url = "https://www.walmart.com/store/directory"
    main = SgRequests.raise_on_err(session.get(url, headers=headers))
    soup = b4(main.text, "lxml")
    allstates = (
        soup.find("div", {"class": "store-directory-container"})
        .find("ul")
        .find_all("a")
    )
    for county in allstates:
        sec = SgRequests.raise_on_err(
            session.get("https://www.walmart.com" + county["href"], headers=headers)
        )
        sec = b4(sec.text, "lxml")
        allcities = (
            sec.find("div", {"class": "store-directory-container"})
            .find("ul")
            .find_all("a")
        )
        for city in allcities:
            if city["href"].count("/") > 2:
                if (
                    str("https://www.walmart.com" + city["href"])
                    == "https://www.walmart.com/store/directory/mo/st.-peters"
                ):
                    state.push_request(SerializableRequest(url="/store/5421"))
                    state.push_request(SerializableRequest(url="/store/5427"))
                    continue
                tri = SgRequests.raise_on_err(
                    session.get(
                        "https://www.walmart.com" + city["href"], headers=headers
                    )
                )
                tri = b4(tri.text, "lxml")
                recs = tri.find("ul", {"class": "store-list-ul"}).find_all(
                    "a", {"class": "storeBanner"}
                )
                for rec in recs:
                    state.push_request(SerializableRequest(url=rec["href"]))
            else:
                state.push_request(SerializableRequest(url=city["href"]))
    return True


def fetch_other(session, state):
    # there's this API for nearby stores.. but nothing for actual store by id "https://www.walmart.com/store/electrode/api/fetch-nearby-stores?store-id={id}"
    for next_r in state.request_stack_iter():
        logger.info(str("https://www.walmart.com" + next_r.url))
        try:
            res = SgRequests.raise_on_err(
                session.get("https://www.walmart.com" + next_r.url, headers=headers)
            )
        except Exception as e:
            if "520" or "404" in str(e):
                try:
                    res = SgRequests.raise_on_err(
                        session.get(
                            "https://www.walmart.com" + next_r.url, headers=headers
                        )
                    )
                except Exception:
                    continue
            else:
                raise Exception
        yield grab_json(b4(res.text, "lxml"))


def vision(x):
    return x


def test_other(session):
    res = SgRequests.raise_on_err(
        session.get("https://www.walmart.com/store/2784-beatrice-ne", headers=headers)
    )
    return grab_json(b4(res.text, "lxml"))


def human_hours(k):
    try:
        if not k["open24Hours"]:
            unwanted = ["open24", "todayHr", "tomorrowHr"]
            h = []
            for day in list(k):
                if not any(i in day for i in unwanted):
                    if k[day]:
                        if "temporaryHour" not in day:
                            if k[day]["closed"]:
                                h.append(str(day).capitalize() + ": Closed")
                            else:
                                if k[day]["openFullDay"]:
                                    h.append(str(day).capitalize() + ": 24Hours")
                                else:
                                    h.append(
                                        str(day).capitalize()
                                        + ": "
                                        + str(k[day]["startHr"])
                                        + "-"
                                        + str(k[day]["endHr"])
                                    )
                        else:
                            if k[day]:
                                h.append("Temporary hours: " + str(k[day].items()))
                    else:
                        h.append(str(day).capitalize() + ": <MISSING>")
            return "; ".join(h)
        else:
            return "24/7"
    except Exception:
        return str(k)


def gen_hours(rec):
    try:
        newrec = rec
        newrec["horas"] = []
        try:
            newrec["horas"].append(
                str("General" + " - " + str(human_hours(rec["operationalHours"])))
            )
        except Exception:
            pass
        for i in rec["primaryServices"]:
            try:
                newrec["horas"].append(
                    str(i["name"] + " - " + str(human_hours(i["operationalHours"])))
                )
            except Exception as e:
                try:
                    newrec["horas"].append(str(i["name"] + " - " + str(e) + "<ERROR>"))
                except Exception:
                    pass
        try:
            for i in rec["secondaryServices"]:
                try:
                    newrec["horas"].append(
                        str(i["name"] + " - " + str(human_hours(i["operationalHours"])))
                    )
                except Exception as e:
                    try:
                        newrec["horas"].append(
                            str(i["name"] + " - " + str(e) + "<ERROR>")
                        )
                    except Exception:
                        pass
        except Exception:
            pass
        if len(newrec["horas"]) > 0:
            newrec["horas"] = "\n".join(newrec["horas"])
        else:
            raise
        return newrec
    except Exception as mf:
        newrec["horas"] = str(mf)
        return newrec


def transform_types(rec):
    try:
        newrec = rec
        types = [
            str(f"({i['id']}) - {i['displayName']};\n") for i in rec["allServices"]
        ]
        types = "".join(types)
        newrec["rawadd"] = types
    except Exception:
        try:
            newrec = rec
            newrec["rawadd"] = (
                str(rec["primaryServices"]) + " " + str(rec["secondaryServices"])
            )
        except Exception:
            newrec = rec
            if newrec:
                newrec["rawadd"] = "<ERROR>"
    return newrec


def please_write(what):
    with open("das.txt", mode="w", encoding="utf-8") as file:
        file.write(str(json.dumps(what)))
        logger.info(what)


def fetch_data():
    state = CrawlStateSingleton.get_instance()
    session = SgRequests(dont_retry_status_codes=set([404, 520]))
    # print(vision(transform_types(test_other(session))["rawadd"])) # noqa
    test = gen_hours(transform_types(test_other(session)))
    please_write(test)
    state.get_misc_value("init", default_factory=lambda: other_source(session, state))
    for item in fetch_other(session, state):
        yield gen_hours(transform_types(item))
    maxZ = search.items_remaining()
    total = 0
    for item in fetch_other(session, state):
        yield gen_hours(transform_types(item))
    for code in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://www.walmart.com/store/finder/electrode/api/stores?singleLineAddr="
            + code
            + "&distance=100"
        )
        try:
            r2 = SgRequests.raise_on_err(session.get(url, headers=headers)).json()
        except Exception:
            r2 = api_get(url, headers, 15, 0, 15).json()
        if r2["payload"]["nbrOfStores"]:
            if int(r2["payload"]["nbrOfStores"]) > 0:
                for store in r2["payload"]["storesData"]["stores"]:
                    if store["geoPoint"]:
                        if store["geoPoint"]["latitude"]:
                            if store["geoPoint"]["longitude"]:
                                search.found_location_at(
                                    store["geoPoint"]["latitude"],
                                    store["geoPoint"]["longitude"],
                                )
                    reczz = gen_hours(transform_types(store))
                    please_write(reczz)
                    yield reczz
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logger.info(f"{code} | found: {found} | total: {total} | progress: {progress}")


def add_walmart(x):
    return x if "Walmart" in x else "Walmart " + x


def scrape():
    url = "https://www.walmart.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["detailsPageURL"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["displayName"],
        ),
        latitude=sp.MappingField(
            mapping=["geoPoint", "latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["geoPoint", "longitude"],
        ),
        street_address=sp.MappingField(
            mapping=["address", "address"],
        ),
        city=sp.MappingField(
            mapping=["address", "city"],
        ),
        state=sp.MappingField(
            mapping=["address", "state"],
        ),
        zipcode=sp.MappingField(
            mapping=["address", "postalCode"],
        ),
        country_code=sp.MappingField(
            mapping=["address", "country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
        ),
        store_number=sp.MappingField(
            mapping=["id"],
        ),
        hours_of_operation=sp.MappingField(mapping=["horas"], is_required=False),
        location_type=sp.MappingField(mapping=["rawadd"], value_transform=vision),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
