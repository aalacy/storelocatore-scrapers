from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
import re
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    session = SgRequests()
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_8()
    )
    base_url = "https://public.api.gdos.salvationarmy.org/search"

    x = 0
    for search_lat, search_lon in search:

        params = {
            "isoCountry": "us",
            "lat": search_lat,
            "lng": search_lon,
            "distanceUnits": "MILES",
            "limit": 30,
        }

        response = session.get(base_url, params=params).json()

        for location in response["objects"]:
            locator_domain = "salvationarmyusa.org"
            country_code = "US"
            store_number = "<MISSING>"
            page_url = (
                "https://public.api.gdos.salvationarmy.org/search?isoCountry=us&lat="
                + str(search_lat)
                + "&lng="
                + str(search_lon)
                + "&distanceUnits=MILES&limit=30"
            )

            location_name = location["name"]
            address = location["address1"]
            if address.split(" ")[0] == "Service":
                address = location["address2"]
            city = location["city"]
            state = location["state"]["shortCode"]
            zipp = location["displayZip"]
            if len(zipp) == 4:
                zipp == "0" + zipp
            phone = location["phoneNumber"]
            if phone == "":
                phone == "<MISSING>"
            else:
                phone = re.sub("[^0-9]", "", str(phone))
                phone = phone[:10]

            if phone == "1800" or phone == "800":
                phone = "1800SATRUCK"
            latitude = location["location"]["latitude"]
            longitude = location["location"]["longitude"]
            search.found_location_at(latitude, longitude)

            try:
                servenum = len(location["services"])
            except Exception:
                servenum = 0

            if servenum > 0:
                for service in location["services"]:
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
                        "location_type": service["category"]["name"],
                        "hours": "<MISSING>",
                        "country_code": country_code,
                    }

            else:
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
                    "location_type": "<MISSING>",
                    "hours": "<MISSING>",
                    "country_code": country_code,
                }

        x = x + 1


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
        store_number=sp.MappingField(mapping=["store_number"]),
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
        duplicate_streak_failure_factor=1000,
    )
    pipeline.run()


scrape()
