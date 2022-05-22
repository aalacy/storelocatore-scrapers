from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8

session = SgRequests()

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA], granularity=Grain_8()
)


def get_data():
    x = 0
    for search_lat, search_lon in search:

        x = x + 1

        url = f"https://www.key.com/loc/DirectorServlet?action=getEntities&entity=BRCH&entity=MCD&lat={search_lat}&lng={search_lon}&distance=100&callback=myJsonpCallback"

        response = session.get(url).text
        response = response.replace("myJsonpCallback(", "")[:-1]

        try:
            response = json.loads(response)
        except Exception:
            continue

        for location in response:
            locator_domain = "key.com"
            page_url = url

            location_properties = location["location"]["entity"]["properties"]
            for loc_property in location_properties:
                if loc_property["name"] == "LocationName":
                    location_name = loc_property["value"]

                if loc_property["name"] == "AddressLine":
                    address = loc_property["value"]

                if loc_property["name"] == "Locality":
                    city = loc_property["value"]

                if loc_property["name"] == "Subdivision":
                    state = loc_property["value"]

                if loc_property["name"] == "PostalCode":
                    zipp = loc_property["value"]

                if loc_property["name"] == "CountryRegion":
                    country_code = loc_property["value"]

                if loc_property["name"] == "LocationID":
                    store_number = loc_property["value"]

                if loc_property["name"] == "Phone1":
                    phone = loc_property["value"]

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

                if loc_property["name"] == "Latitude":
                    latitude = loc_property["value"]

                if loc_property["name"] == "Longitude":
                    longitude = loc_property["value"]

                if loc_property["name"] == "HoursOfOperation":
                    hours_list = loc_property["value"].replace(" - ", "-").split(" ")
                    x = 0
                    hour_values = []
                    days = []
                    for item in hours_list:
                        if x % 2 == 0:
                            hour_values.append(item)
                        else:
                            days.append(item)

                        x = x + 1

                    hours = ""
                    for index in range(len(days)):
                        hours = hours + days[index] + " " + hour_values[index] + ", "

            if zipp == "99999":
                zipp = "<MISSING>"

            if address == "Tbd":
                continue

            search.found_location_at(latitude, longitude)

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
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
        duplicate_streak_failure_factor=100000,
    )
    pipeline.run()


scrape()
