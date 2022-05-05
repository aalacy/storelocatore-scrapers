from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_2
import json
import time


def get_data():
    search = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.BRITAIN,
        ],
        expected_search_radius_miles=4,
        granularity=Grain_2(),
    )
    session = SgRequests()
    api_keys = [
        "js3Mzn9chq5ZCMWiJCn2rcE86pJSE7Kt",
        "LZplP41M9JQ0tJq2obNgMoGIs4sgaERl",
        "mf5aDbbRmWv6tHZeu73zGz9yWX1sQ0WR",
        "d7pRKCRzcXWGUzYkQ4xHL8A2IUX9zKWJ",
    ]
    x = 0
    for search_lat, search_lon in search:
        x = x + 1
        api_key = api_keys[x % 4]
        url = (
            "https://transit.land/api/v1/stops?lon="
            + str(search_lon)
            + "&lat="
            + str(search_lat)
            + "&r=10000&apikey="
            + api_key
            + "&per_page=100000"
        )

        try:
            response = session.get(url).json()

        except Exception:
            time.sleep(0.5)
            x = x + 1
            api_key = api_keys[x % 4]
            url = (
                "https://transit.land/api/v1/stops?lon="
                + str(search_lon)
                + "&lat="
                + str(search_lat)
                + "&r=10000&apikey="
                + api_key
                + "&per_page=100000"
            )
            response = session.get(url).json()

        if len(response["stops"]) == 0:
            time.sleep(0.5)
        for location in response["stops"]:
            try:
                page_url = location["tags"]["stop_url"]

            except Exception:
                page_url = "<MISSING>"

            try:
                location_name = "<MISSING>" + "-" + location["name"]

            except Exception:
                continue
            address = location["name"]
            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            latitude = location["geometry"]["coordinates"][1]
            longitude = location["geometry"]["coordinates"][0]
            search.found_location_at(latitude, longitude)

            try:
                store_number = (
                    location["operators_serving_stop"][0]["operator_name"]
                    + "_"
                    + location["onestop_id"]
                )

            except Exception:
                continue
            hours = "<MISSING>"
            phone = "<MISSING>"
            location_type_parts = location["served_by_vehicle_types"]

            location_type = ""
            for part in location_type_parts:
                location_type = location_type + str(part) + ","

            location_type = location_type[:-1]

            yield {
                "page_url": page_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": address,
                "state": state,
                "zip": zipp,
                "phone": phone,
                "location_type": location_type,
                "hours": hours,
            }


def scrape():

    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(
            "https://www.transit.land/documentation/datastore/stops#stops-api"
        ),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.ConstantField("<MISSING>"),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
