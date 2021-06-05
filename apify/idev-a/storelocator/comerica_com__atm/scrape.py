from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_2
from sglogging import SgLogSetup
from requests import exceptions  # noqa
from urllib3 import exceptions as urllibException
from bs4 import BeautifulSoup as bs
import json

logger = SgLogSetup().get_logger("comerica_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA], granularity=Grain_2()
)


def api_get(start_url, headers, timeout, attempts, maxRetries):
    error = False
    session = SgRequests()
    try:
        results = session.get(start_url, headers=headers, timeout=timeout)
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
            results = api_get(start_url, headers, timeout, attempts, maxRetries)
        else:
            TooManyRetries = (
                "Retried "
                + str(maxRetries)
                + " times, got either SSLError or ProxyError"
            )
            raise TooManyRetries
    else:
        return results


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for code in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0
        page = 1
        logger.info(("Pulling Zip Code %s..." % code))
        while True:
            url = f"https://locations.comerica.com/?q={code}&filter=bc&filter=atm&filter=itm&filter=drive&page={page}"
            try:
                res = session.get(url, headers=headers, timeout=15).text
            except Exception:
                res = api_get(url, headers, 15, 0, 15).text

            if "Comerica Bank is not in your area." in res:
                logger.info(f"not found {code} | page {page} ")
                break
            if "You have exceeded the maximum number of allowed searches." in res:
                logger.info("Proxy not working")
                break
            soup = bs(res, "lxml")
            try:
                r2 = json.loads(
                    res.split("var results = ")[1]
                    .strip()
                    .split("var map;")[0]
                    .strip()[:-1]
                )
            except:
                break
            for _ in r2:
                search.found_location_at(
                    _["location"]["lat"],
                    _["location"]["lng"],
                )
                for store in _["location"]["entities"]:
                    store["state"] = _["location"]["province"]
                    store["city"] = _["location"]["city"]
                    store["street"] = _["location"]["street"]
                    store["country"] = _["location"]["country"]
                    store["lat"] = _["location"]["lat"]
                    store["lng"] = _["location"]["lng"]
                    store["postal_code"] = _["location"]["postal_code"]
                    if "name" in store:
                        name = "-".join(
                            [
                                nn
                                for nn in store.get("name")
                                .lower()
                                .replace(" - ", "-")
                                .replace(" & ", "-")
                                .replace(",", "")
                                .replace(".", "")
                                .replace("/", "")
                                .replace("(", "")
                                .replace(")", "")
                                .split(" ")
                                if nn.strip()
                            ]
                        )
                        store[
                            "page_url"
                        ] = f"https://locations.comerica.com/location/{name}"
                    elif store["type"] == "atm" and store["cma_id"]:
                        store["name"] = store["type"] + store["street"]
                        store[
                            "page_url"
                        ] = f"https://locations.comerica.com/location/{store['type'].lower()}-{store['cma_id'].lower()}"

                    else:
                        continue
                    store["hours"] = human_hours(store["open_hours_formatted"])
                    if "page_url" in store:
                        soup1 = bs(
                            session.get(
                                store["page_url"], headers=headers, timeout=15
                            ).text,
                            "lxml",
                        )
                        h3_tag = soup1.select_one('h3[property="name"]')
                        try:
                            if h3_tag.find_next_sibling("p"):
                                store["hours"] = "Temporarily closed"
                        except:
                            pass

                    yield store
                    found += 1
            total += found
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            cur_page = 0
            if soup.select_one("ul.pager li.pager-current span"):
                cur_page = int(
                    soup.select_one("ul.pager li.pager-current span")
                    .text.split("of")[-1]
                    .strip()
                )

            logger.info(
                f"{code} | page {page} | found: {found} | total: {total} | progress: {progress}"
            )
            page += 1
            if page > cur_page:
                break


def human_phone(val):
    if val:
        return val.strip()
    else:
        return "<MISSING>"


def human_hours(k):
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    if k.get("lobby"):
        hours = []
        for x, _ in enumerate(k["lobby"]):
            time = _
            if not _:
                time = "closed"
            hours.append(f"{days[x]}: {time}")
        return "; ".join(hours)
    else:
        return "<MISSING>"


def scrape():
    url = "https://www.comerica.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["page_url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MappingField(
            mapping=["street"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["postal_code"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
            raw_value_transform=human_phone,
        ),
        store_number=sp.MappingField(
            mapping=["id"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(
            mapping=["type"],
            part_of_record_identity=True,
        ),
        raw_address=sp.MissingField(),
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
