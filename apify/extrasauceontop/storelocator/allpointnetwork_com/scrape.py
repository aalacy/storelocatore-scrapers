from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    searches = [
        static_coordinate_list(country_code=SearchableCountries.USA, radius=50),
        static_coordinate_list(country_code=SearchableCountries.USA, radius=50),
        static_coordinate_list(country_code=SearchableCountries.USA, radius=50),
    ]
    url = "https://clsws.locatorsearch.net/Rest/LocatorSearchAPI.svc/GetLocations"
    session = SgRequests()

    for search in searches:
        for search_lat, search_lon in search:

            params = {
                "Latitude": str(search_lat),
                "Longitude": str(search_lon),
                "Miles": "100",
                "NetworkId": "10029",
                "PageIndex": "1",
                "SearchByOptions": "",
            }

            response = session.post(url, json=params).json()

            try:
                for location in response["data"]["ATMInfo"]:
                    locator_domain = "allpointnetwork.com"
                    page_url = "https://clsws.locatorsearch.net/Rest/LocatorSearchAPI.svc/GetLocations"
                    location_name = "Allpoint " + location["RetailOutlet"]
                    print(location_name)
                    address = location["Street"]
                    city = location["City"]
                    state = location["State"]
                    zipp = location["ZipCode"]
                    country_code = location["Country"]
                    if country_code == "MX":
                        continue
                    store_number = location["LocationID"]
                    phone = "<MISSING>"
                    location_type = location["RetailOutlet"]
                    latitude = location["Latitude"]
                    longitude = location["Longitude"]
                    search.found_location_at(latitude, longitude)
                    hours = "<MISSING>"

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

            except Exception:
                pass


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
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
    )
    pipeline.run()


scrape()
