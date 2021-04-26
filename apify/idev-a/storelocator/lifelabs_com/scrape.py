from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from requests import exceptions  # noqa
from urllib3 import exceptions as urllibException

logger = SgLogSetup().get_logger("mycarecompass")

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "Host": "on-api.mycarecompass.lifelabs.com",
    "Origin": "https://locations.lifelabs.com",
    "Referer": "https://locations.lifelabs.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def payload(address):
    return {
        "address": str(address),
        "locationCoordinate": {"latitude": "0", "longitude": "0"},
        "locationFinderSearchFilters": {
            "isOpenEarlySelected": False,
            "isOpenWeekendsSelected": False,
            "isOpenSundaysSelected": False,
            "isWheelchairAccessibleSelected": False,
            "isDoesECGSelected": False,
            "isDoes24HourHolterMonitoringSelected": False,
            "isDoesAmbulatoryBloodPressureMonitoringSelected": False,
            "isDoesServeAutismSelected": False,
            "isGetCheckedOnlineSelected": False,
            "isOpenSaturdaysSelected": False,
            "isCovid19TestingSiteSelected": False,
        },
    }


search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
    max_search_results=None,
)


def api_post(start_url, headers, data, timeout, attempts, maxRetries):
    error = False
    session = SgRequests()
    try:
        results = session.post(start_url, headers=headers, json=data, timeout=timeout)
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
            results = api_post(start_url, headers, data, timeout, attempts, maxRetries)
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
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://on-api.mycarecompass.lifelabs.com/api/LocationFinder/GetLocations/"
        )
        try:
            res = session.post(
                url, headers=headers, json=payload(code), timeout=15
            ).json()
        except Exception:
            res = api_post(url, headers, payload(code), 15, 0, 15).json()

        if not res or not res["entity"]:
            continue

        for _ in res["entity"]:
            search.found_location_at(
                _["locationCoordinate"]["latitude"],
                _["locationCoordinate"]["longitude"],
            )
            _["state"] = _["locationAddress"]["province"]
            _["city"] = _["locationAddress"]["city"]
            _["postal_code"] = _["locationAddress"]["postalCode"]
            _["street"] = _["locationAddress"]["street"].split("-")[-1]
            _["country"] = "CA"
            _["lat"] = _["locationCoordinate"]["latitude"]
            _["lng"] = _["locationCoordinate"]["longitude"]
            yield _
            found += 1
        total += found
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"{code} | found: {found} | total: {total} | progress: {progress}")


def human_hours(k):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = []
    for x, _ in enumerate(k):
        time = f"{_['openTime']}-{_['closeTime']}"
        if not _["closeTime"] and not _["openTime"]:
            time = "closed"
        hours.append(f"{days[x]}: {time}")
    return "; ".join(hours)


def scrape():
    url = "https://www.lifelabs.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MissingField(),
        location_type=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["pscName"],
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
        phone=sp.MappingField(mapping=["phone"], part_of_record_identity=True),
        store_number=sp.MappingField(
            mapping=["locationId"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hoursOfOperation"], raw_value_transform=human_hours
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
