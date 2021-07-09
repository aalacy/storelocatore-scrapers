from sgrequests import SgRequests
import time
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "content-type": "application/json",
        "origin": "https://www.transit.land",
        "referer": "https://www.transit.land/",
    }
    session = SgRequests(retry_behavior=False)
    x = 0

    onestop_ids = []
    while True:
        params = {
            "operationName": "",
            "variables": {"search": "", "merged": False, "limit": 1000, "after": x},
            "query": "query ($limit: Int, $after: Int, $search: String, $merged: Boolean) {\n  entities: operators(\n    after: $after\n    limit: $limit\n    where: {search: $search, merged: $merged}\n  ) {\n    id\n    agency_name\n    operator_name\n    operator_short_name\n    onestop_id\n    city_name\n    adm1name\n    adm0name\n    places_cache\n    agency {\n      places(where: {min_rank: 0.2}) {\n        name\n        adm0name\n        adm1name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        }

        url = "https://demo.transit.land/api/v2/query"
        response = session.post(url, json=params, headers=headers).json()

        if len(response["data"]["entities"]) == 0:
            break

        for location in response["data"]["entities"]:
            if (
                location["adm0name"] == "United States of America"
                or location["adm0name"] == "Ireland"
                or location["adm0name"] == "United Kingdom"
                or location["adm0name"] == "Canada"
            ):
                onestop_ids.append(location["onestop_id"])

        x = x + 1000

    x = 0
    api_keys = [
        "js3Mzn9chq5ZCMWiJCn2rcE86pJSE7Kt",
        "LZplP41M9JQ0tJq2obNgMoGIs4sgaERl",
        "mf5aDbbRmWv6tHZeu73zGz9yWX1sQ0WR",
    ]
    for onestop_id in onestop_ids:
        offset = 0
        x = x + 1

        api_key = api_keys[x % 3]
        while True:

            y = 0
            while True:
                y = y + 1
                if y == 11:
                    break
                try:
                    url = (
                        "https://api.transit.land/api/v1/stops?apikey="
                        + api_key
                        + "&offset="
                        + str(offset)
                        + "&per_page=500&sort_key=id&sort_order=asc&served_by="
                        + onestop_id
                    )
                    response = session.get(url, timeout=1000)
                    response_code = response.status_code
                    response = response.json()
                    break
                except Exception:
                    continue

            if response_code == 404:
                time.sleep(0.5)
            try:
                if len(response["stops"]) == 0:
                    break
            except Exception:
                break

            for location in response["stops"]:
                try:
                    page_url = location["tags"]["stop_url"]

                except Exception:
                    page_url = "<MISSING>"

                location_name = (
                    location["operators_serving_stop"][0]["operator_name"]
                    + "-"
                    + location["name"]
                )
                address = location["name"]
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
                latitude = location["geometry"]["coordinates"][1]
                longitude = location["geometry"]["coordinates"][0]
                store_number = (
                    location["operators_serving_stop"][0]["operator_name"]
                    + "_"
                    + location["onestop_id"]
                )
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

            if len(response["stops"]) < 500:
                break

            else:
                offset = offset + 500


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
