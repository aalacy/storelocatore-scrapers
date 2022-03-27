from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("manpower")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.manpower.com"
base_url = "https://www.manpower.com/ManpowerUSA/home"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=500,
    max_search_results=None,
)


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    res = session.get(base_url, headers=_headers)
    url = (
        locator_domain
        + res.headers["Content-Location"]
        + res.text.split("var findLocationURL =")[1].split("function")[0].strip()[1:-2]
    )
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % lat, lng))
        page_url = f"{url}?id={lat},{lng}"
        logger.info(page_url)
        locations = json.loads(
            session.get(page_url, headers=_headers)
            .text.split("function setMap(){")[1]
            .split("locations1=")[1]
            .split("var mapOptions")[0]
            .strip()[:-1]
        )
        total += len(locations)
        for _ in locations:
            search.found_location_at(
                _[-3],
                _[-2],
            )
            store = {}
            store["lat"] = str(_[-3])
            store["lng"] = str(_[-2])
            store["street"] = (_[1] + " " + _[2]).strip().replace("&amp;", "&")
            if store["street"] == "-":
                store["street"] = "<MISSING>"
            store["name"] = _[0]
            store["state"] = _[5].split(",")[1].strip().split(" ")[0].strip()
            store["city"] = (
                _[3].replace("&#039;", "'").replace(store["state"], "").strip()
            )
            store["zip_postal"] = _[5].split(",")[1].strip().split(" ")[1].strip()
            store["country"] = _[4]
            store["phone"] = _[6].strip() or "<MISSING>"
            if store["phone"] == "-" or store["phone"] == "x":
                store["phone"] = "<MISSING>"
            store["phone"] = store["phone"].split("x")[0]
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MissingField(),
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
            mapping=["street"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["zip_postal"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MissingField(),
        store_number=sp.MissingField(),
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
