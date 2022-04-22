from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from requests import exceptions  # noqa
from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
import math
import ssl
import os

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(
    ssl, "_create_unverified_context", None
):
    ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("walmart_com")

headers = {}
headers[
    "accept"
] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
headers["accept-encoding"] = "gzip, deflate, br"
headers["accept-language"] = "en-US,en;q=0.9,ro;q=0.8,es;q=0.7"
headers["cache-control"] = "no-cache"
headers["pragma"] = "no-cache"
headers["sec-ch-ua-mobile"] = "?1"
headers["sec-ch-ua-platform"] = '"Android"'
headers["sec-fetch-dest"] = "document"
headers["sec-fetch-mode"] = "navigate"
headers["sec-fetch-site"] = "none"
headers["sec-fetch-user"] = "?1"
headers["upgrade-insecure-requests"] = "1"
headers[
    "user-agent"
] = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Mobile Safari/537.36"

search = DynamicGeoSearch(
    country_codes=SearchableCountries.ALL,
    expected_search_radius_miles=80,
)


def api_get(url, session):
    try:
        res = SgRequests.raise_on_err(session.get(url, headers=headers))
    except Exception as e:
        if "520" or "404" in str(e):
            try:
                res = SgRequests.raise_on_err(session.get(url, headers=headers))
            except Exception as f:
                logger.error(url)
                logger.error(f"{str(f)}{str(e)}")
                raise Exception
        else:
            logger.error(url)
            logger.error(f"{str(e)}")
            raise Exception
    return res.json()


def other_source(urlz, size, state):
    for county in range(2, size, 1):
        state.push_request(SerializableRequest(url=urlz.format(county)))
    return True


def fetch_other(session, state):
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        res = api_get(next_r.url, session)
        yield res


def fetch_data():
    state = CrawlStateSingleton.get_instance()
    urlW = "http://location.westernunion.com/api/locations?lat={}&lng={}&page={}"
    session = SgRequests(dont_retry_status_codes=set([404, 520]), verify_ssl=False)
    maxZ = search.items_remaining()
    total = 0
    for coord in search:
        lat, lng = coord
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0
        logger.info(("Pulling coord Code %s..." % str(coord)))
        url = urlW.format(round(lat, 6), round(lng, 6), "{}")
        data = api_get(url.format(1), session)
        for rec in data["results"]:
            yield rec
            if rec["latitude"]:
                if rec["longitude"]:
                    search.found_location_at(rec["latitude"], rec["longitude"])
        other_source(url, int(math.ceil(data["resultCount"] / 15)), state)
        for rec in fetch_other(session, state):
            for store in rec["results"]:
                yield store
                if store["latitude"]:
                    if store["longitude"]:
                        search.found_location_at(store["latitude"], store["longitude"])
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logger.info(f"{coord} | found: {found} | total: {total} | progress: {progress}")


def human_hours(k):
    try:
        hours = []
        for i in list(k["desktopHours"].items()):
            hours.append(str(i[0]) + ": " + str(i[1]))
        return "; ".join(hours)
    except Exception:
        return str(k)


def add_walmart(x):
    return x if "Walmart" in x else "Walmart " + x


def scrape():
    url = "https://www.westernunion.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["name"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            is_required=False,
        ),
        street_address=sp.MappingField(
            mapping=["streetAddress"],
            is_required=False,
        ),
        city=sp.MappingField(
            mapping=["city"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["state"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["postal"],
            is_required=False,
        ),
        country_code=sp.MappingField(
            mapping=["country"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["s_phone"],
            part_of_record_identity=True,
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["orig_id"],
            part_of_record_identity=True,
            is_required=False,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["desktopHours"],
            raw_value_transform=human_hours,
            is_required=False,
        ),
        location_type=sp.MappingField(
            mapping=["type"],
            is_required=False,
        ),
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
