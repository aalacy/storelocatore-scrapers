from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser
import json

logger = SgLogSetup().get_logger("penn-station_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
headers["Content-Type"] = "application/x-www-form-urlencoded"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
    max_search_distance_miles=100,
    max_search_results=15,
)


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
    if k:
        return k
    else:
        return {
            "country": "",
            "address": "",
            "city": "",
            "state": "",
            "zip": "",
            "raw_address": "",
        }


def fetch_data():
    session = SgRequests()
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

        r2 = session.post(url, headers=headers, data=data)
        decoded_data = r2.text.encode().decode("utf-8-sig")
        r2 = json.loads(decoded_data)

        if r2["success"] == 1:
            for store in r2["stores"]:
                if store["lat"]:
                    if store["lng"]:
                        search.found_location_at(
                            store["lat"],
                            store["lng"],
                        )
                store.update(parse_address(store["address"]))
                if store:
                    found += 1
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
            is_required=False,
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
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
