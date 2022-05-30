from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
from sgscrape import simple_scraper_pipeline as sp

session = SgRequests()
search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    granularity=Grain_8(),
    expected_search_radius_miles=45,
)


def get_data():
    x = 0
    for search_lat, search_lon in search:

        x = x + 1

        url = f"https://www.key.com/loc/DirectorServlet?action=getEntities&entity=ATM&lat={search_lat}&lng={search_lon}&distance=1000&callback=myJsonpCallback"

        response = session.get(url).text
        response = response.replace("myJsonpCallback(", "")[:-1]

        try:
            response = json.loads(response)
        except Exception:
            continue

        for location in response:
            locator_domain = "key.com"
            page_url = "https://www.key.com/locations/search"

            location_properties = location["properties"]
            location_name = location_properties["LocationName"]
            address = location_properties["AddressLine"]
            city = location_properties["Address"]["city"]
            state = location_properties["Address"]["state"]
            zipp = location_properties["Address"]["zipCode"]
            country_code = location_properties["CountryRegion"]
            store_number = location_properties["LocationID"]
            phone = location_properties["Phone1"]
            latitude = location_properties["Latitude"]
            longitude = location_properties["Longitude"]
            search.found_location_at(latitude, longitude)
            hours = location_properties["HoursOfOperation"]

            loc_props = location["location"]["entity"]["properties"]
            for loc_property in loc_props:
                if loc_property["name"] == "LocationType":
                    location_type = loc_property["value"]
                    if location_type == "BRCH":
                        location_type = "branch"
                    elif location_type == "ATM":
                        location_type = "ATM"
                    elif location_type == "MCD":
                        location_type = "Key Private Bank"
                    else:
                        location_type = "<MISSING>"

                    if (
                        location_type == "ATM"
                        and store_number.replace("ATM", "")[:2] == "KB"
                    ):
                        location_type = "KeyBank ATM"

                    elif (
                        location_type == "ATM"
                        and store_number.replace("ATM", "")[:2] != "KB"
                    ):
                        location_type = "Partner ATM"

            yield {
                "locator_domain": locator_domain,
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
                "country_code": country_code,
            }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(
            mapping=["location_type"], part_of_record_identity=True
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
        duplicate_streak_failure_factor=-1,
    )
    pipeline.run()


scrape()
