from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser
from requests import exceptions  # noqa
from urllib3 import exceptions as urllibException

logger = SgLogSetup().get_logger("penn-station_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
headers["Content-Type"] = "application/x-www-form-urlencoded"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
    max_radius_miles=100,
    max_search_results=15,
)


def api_get(start_url, headers, data, attempts, maxRetries):
    error = False
    session = SgRequests()
    try:
        results = session.post(start_url, headers=headers, data=data)
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
            results = api_get(start_url, headers, data, attempts, maxRetries)
        else:
            TooManyRetries = (
                "Retried "
                + str(maxRetries)
                + " times, got either SSLError or ProxyError"
            )
            raise TooManyRetries
    else:
        return results


def parse_address(raw_address):
    k = {}
    parsed = parser.parse_address_usa(raw_address)
    k["country"] = parsed.country if parsed.country else "<MISSING>"
    k["address"] = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
    k["address"] = (
        (k["address"] + ", " + parsed.street_address_2)
        if parsed.street_address_2
        else k["address"]
    )
    k["city"] = parsed.city if parsed.city else "<MISSING>"
    k["state"] = parsed.state if parsed.state else "<MISSING>"
    k["zip"] = parsed.postcode if parsed.postcode else "<MISSING>"
    k["raw_address"] = raw_address

    return k


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0
        url = "https://www.penn-station.com/storefinder_responsive/index.php"
        data = "ajax=1&action=get_nearby_stores&distance=1000&lat={lat}&lng={lng}&products=1".format(
            lat=lat, lng=lng
        )
        try:
            r2 = session.post(url, headers=headers, data=data).json()
        except Exception:
            r2 = api_get(url, headers, data, 0, 15).json()

        if r2["success"] == 1:
            for store in r2["stores"]:
                if store["lat"]:
                    if store["lng"]:
                        search.found_location_at(
                            store["lat"],
                            store["lng"],
                        )
                store = store.update(parse_address(store["address"]))
                if store is not None:
                    yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logger.info(
            f"{lat} & {lng} | found: {found} | total: {total} | progress: {progress}"
        )


def scrape():
    url = "https://penn-station.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["website"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["address"],
            part_of_record_identity=True,
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["zip"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["telephone"],
            part_of_record_identity=True,
        ),
        store_number=sp.MappingField(
            mapping=["website"],
            value_transform=lambda x: x.rsplit("/", 1)[-1].strip(),
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(
            mapping=["cat_name"],
        ),
        raw_address=sp.MappingField(
            mapping=["raw_address"],
        ),
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
