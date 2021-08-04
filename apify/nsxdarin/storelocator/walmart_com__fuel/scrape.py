from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from urllib3 import exceptions as urllibException

logger = SgLogSetup().get_logger("walmart_com/fuel")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    expected_search_radius_miles=None,
    max_search_results=50,
)


def api_get(start_url, headers, timeout, attempts, maxRetries):
    error = False
    session = SgRequests()
    try:
        results = session.get(start_url, headers=headers, timeout=timeout)

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
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for code in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://www.walmart.com/store/finder/electrode/api/stores?singleLineAddr="
            + code
            + "&distance=50"
        )
        try:
            r2 = session.get(url, headers=headers, timeout=15).json()
        except:
            r2 = api_get(url, headers, 15, 0, 15).json()
        if r2["payload"]["nbrOfStores"]:
            if int(r2["payload"]["nbrOfStores"]) > 0:
                for store in r2["payload"]["storesData"]["stores"]:
                    if store["geoPoint"] and "GAS" in str(store):
                        if store["geoPoint"]["latitude"]:
                            if store["geoPoint"]["longitude"]:
                                search.found_location_at(
                                    store["geoPoint"]["latitude"],
                                    store["geoPoint"]["longitude"],
                                )
                    yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logger.info(f"{code} | found: {found} | total: {total} | progress: {progress}")


def human_hours(k):
    AllTheHours = k
    for hrSet in AllTheHours:
        if (
            hrSet["id"] == 851
            or hrSet["id"] == 17
            or "GAS" in hrSet["name"]
            or "FUEL" in hrSet["name"]
        ):
            k = hrSet["operationalHours"]
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
                return (
                    "; ".join(h)
                    .replace("Montofrihrs", "Mon-Fri")
                    .replace("hrs:", ":")
                    .replace("; Temporaryhours: <MISSING>", "")
                )
            else:
                return "24/7"


def add_walmart(x):
    return x if "Walmart" in x else "Walmart " + x


def scrape():
    url = "https://www.walmart.com/vision"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["detailsPageURL"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["storeType", "name"],
            value_transform=add_walmart,
        ),
        latitude=sp.MappingField(
            mapping=["geoPoint", "latitude"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["geoPoint", "longitude"],
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["address", "address"],
            part_of_record_identity=True,
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
            part_of_record_identity=True,
        ),
        store_number=sp.MappingField(
            mapping=["id"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["featuredServices"],
            raw_value_transform=human_hours,
            is_required=False,
        ),
        location_type=sp.MappingField(
            mapping=["featuredServices"],
            value_transform=lambda x: "Fuel"
            if any(i in str(x) for i in ["FUEL", "GAS"])
            else "<MISSING>",
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
